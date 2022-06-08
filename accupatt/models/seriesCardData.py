import matplotlib
import numpy as np
import pandas as pd
from scipy import interpolate
import accupatt.config as cfg
from accupatt.models.passCardData import PassCardData
from accupatt.models.passData import Pass
from accupatt.widgets.mplwidget import MplWidget
from PyQt6.QtWidgets import QTableWidget
from scipy.stats import variation


class SeriesCardData:
    def __init__(self, passes: list[Pass], target_swath, swath_units: str):
        # Live feeds from Series Object
        self.passes = passes
        self.swath_units = swath_units
        self.swath_adjusted = target_swath if target_swath > 0 else 50
        # Options
        # self.smooth = True
        # self.smooth_window = cfg.get_string_smooth_window()
        # self.smooth_order = cfg.get_string_smooth_order()
        # self.equalize_integrals = True
        self.center = True
        self.center_method = cfg.get_center_method()
        self.simulated_adjascent_passes = 2

    def set_swath_adjusted(self, string) -> bool:
        try:
            int(float(string))
        except ValueError:
            return False
        self.swath_adjusted = int(float(string))
        return True
    
    def _get_active_passes(self) -> list[Pass]:
        activePasses: list[Pass] = []
        for p in self.passes:
            if not p.has_card_data():
                continue
            if not p.cards_include_in_composite:
                continue
            if not any([sc.include_in_composite for sc in p.cards.card_list]):
                continue
            activePasses.append(p)
        return activePasses

    def _get_average(self) -> pd.DataFrame:
        
        dd = pd.DataFrame()
        lastPassName = ""
        for p in self._get_active_passes():
            # Get Pass Dataframe
            d = p.cards.get_data_mod(loc_units=self.swath_units)
            # Start or merge to the series dataframe
            if dd.empty:
                dd = d
            else:
                dd = dd.merge(d.set_index("loc"), on="loc", how="outer", suffixes=[f"_{lastPassName}",f"_{p.name}"])
            lastPassName = p.name
        if dd.empty:
            return dd
        dd.set_index("loc", inplace=True)
        dd.sort_values(by="loc", axis=0, inplace=True)
        dd.interpolate(method="slinear", limit_area="inside", inplace=True)
        dd.fillna(0, inplace=True)
        dd["cov_avg"] = dd.loc[:,dd.columns.str.contains('cov')].mean(axis="columns")
        dd["dv01_avg"] = dd.loc[:,dd.columns.str.contains('dv01')].mean(axis="columns")
        dd["dv05_avg"] = dd.loc[:,dd.columns.str.contains('dv05')].mean(axis="columns")
        dd["loc_units"] = [self.swath_units for i in range(len(dd.index))]
        avg = dd.loc[:,["cov_avg","dv01_avg","dv05_avg","loc_units"]].reset_index()
        avg.rename(columns={"cov_avg":"cov","dv01_avg":"dv01","dv05_avg":"dv05"}, inplace=True)
        return avg

    def plotOverlay(self, mplWidget: MplWidget):
        # Setup and clear the plotter
        self._config_mpl_plotter(mplWidget)
        mplWidget.canvas.ax.set_ylabel("Coverage")
        mplWidget.canvas.ax.yaxis.set_major_formatter(
            matplotlib.ticker.PercentFormatter(xmax=100, decimals=0)
        )
        active_passes = self._get_active_passes()
        # Iterate over plottable passes
        for p in active_passes:
            data = p.cards.get_data_mod(loc_units=self.swath_units)
            # Numpy-ize dataframe columns to plot
            x = np.array(data["loc"], dtype=float)
            y = np.array(data["cov"], dtype=float)
            # Plot non-zero data, and label the series with the pass name
            mplWidget.canvas.ax.plot(x[y != 0],
                                     y[y != 0],
                                     linewidth=1,
                                     label=p.name)
        # Add a legend if applicable
        if len(active_passes) > 1:
            mplWidget.canvas.ax.legend()
        # Must set ylim after plotting
        mplWidget.canvas.ax.set_ylim(bottom=0, auto=None)
        # Draw the plot regardless if passes were plotted to it
        mplWidget.canvas.draw()

    def plotAverage(self, mplWidget: MplWidget, colorize: bool):
        # Setup and clear the plotter
        self._config_mpl_plotter(mplWidget)

        avg = self._get_average()
        if avg.empty:
            return
        avgPass = PassCardData()
        avgPass.center = self.center
        avgPass.center_method = self.center_method
        avg = avgPass.get_data_mod(loc_units=self.swath_units, data=avg)
        # Must re-add loc_units, as it is stripped during get_data_mod
        avg["loc_units"] = pd.Series(
            [self.swath_units for i in range(len(avg.index))], dtype=str
        )
        avgPass.plotCoverage(
            mplWidget=mplWidget, loc_units=self.swath_units, colorize=colorize, d=avg
        )
        if cfg.get_card_plot_average_swath_box():
            # Find average deposition inside swath width
            swath_width = self.swath_adjusted
            a_c = avg[(avg["loc"] >= -swath_width/2) & (avg["loc"] <= swath_width/2)]
            a_c_mean = a_c["cov"].mean(axis="rows")
            mplWidget.canvas.ax.plot(
                    [-swath_width/2, -swath_width/2, swath_width/2, swath_width/2],
                    [0, a_c_mean/2, a_c_mean/2, 0],
                    color="black",
                    linewidth=1,
                    dashes=(3,2),
                    label="Effective Swath"
                )
            if not colorize:
                mplWidget.canvas.ax.legend()
            # Must set ylim after plotting
            mplWidget.canvas.ax.set_ylim(bottom=0, auto=None)
            # Plot it
            mplWidget.canvas.draw()

    def _config_mpl_plotter(self, mplWidget: MplWidget):
        mplWidget.canvas.ax.clear()
        mplWidget.canvas.ax.set_xlabel(f"Location ({self.swath_units})")

    def plotRacetrack(
        self, mplWidget: MplWidget, swath_width: float, showEntireWindow=False
    ):
        self._plotSimulation(
            mplWidget, swath_width, showEntireWindow, label="Racetrack"
        )

    def plotBackAndForth(
        self, mplWidget: MplWidget, swath_width: float, showEntireWindow=False
    ):
        self._plotSimulation(
            mplWidget,
            swath_width,
            showEntireWindow,
            mirrorAdjascent=True,
            label="Back & Forth",
        )

    def _plotSimulation(
        self,
        mplWidget: MplWidget,
        swath_width: float,
        showEntireWindow=False,
        mirrorAdjascent=False,
        label="",
    ):
        # Setup and clear the plotter
        self._config_mpl_plotter(mplWidget)
        # Convenience accessor to average string modified data

        avg = self._get_average()
        avgPass = PassCardData()
        avgPass.center = self.center
        avgPass.center_method = self.center_method
        a = avgPass.get_data_mod(loc_units=self.swath_units, data=avg)
        if not a.empty:
            # Original average data
            x0 = np.array(a["loc"], dtype=float)
            y0 = np.array(a["cov"], dtype=float)
            # create a shifted x array for each simulated pass with labels
            x_arrays = [x0]
            y_arrays = [y0]
            labels = ["Center"]
            for i in range(1, self.simulated_adjascent_passes + 1):
                x = (x0 * -1)[::-1] if mirrorAdjascent and i % 2 != 0 else x0
                y = y0[::-1] if mirrorAdjascent and i % 2 != 0 else y0
                x_arrays.append(x - (i * swath_width))
                y_arrays.append(y)
                labels.append(f"Left {i}")
                x_arrays.append(x + (i * swath_width))
                y_arrays.append(y)
                labels.append(f"Right {i}")
            # Unify the x-domain
            xfill = np.sort(np.concatenate(x_arrays))
            # Interpolate the original y-values to the new x-domain
            y_fills = []
            for i in range(len(x_arrays)):
                y_fills.append(
                    np.interp(xfill, x_arrays[i], y_arrays[i], left=0, right=0)
                )
            # Plot the fills cumulatively in order of generation: C, L1, R1, L2, R2, etc.
            y_fill_cum = np.zeros(xfill.size)
            for i in range(len(y_fills)):
                mplWidget.canvas.ax.fill_between(
                    xfill, 
                    y_fill_cum, 
                    y_fill_cum + y_fills[i], 
                    alpha=0.7,
                    label=labels[i]
                )
                y_fill_cum = y_fill_cum + y_fills[i]
            # Plot a solid line on the cumulative deposition
            mplWidget.canvas.ax.plot(xfill, y_fill_cum, color="black")
            # Find average deposition inside swath width
            avg = np.mean(
                y_fill_cum[
                    np.where(((xfill >= -swath_width / 2) & (xfill <= swath_width / 2)))
                ]
            )
            mplWidget.canvas.ax.plot(
                [-swath_width / 2, swath_width / 2],
                [avg, avg],
                color="black",
                dashes=[3, 2],
                label="Mean Dep.",
            )
            # Legend
            mplWidget.canvas.ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
            # Y Label
            mplWidget.canvas.ax.set_ylabel(label)
            # Whether to show the whole window or one swath width
            if not showEntireWindow:
                mplWidget.canvas.ax.set_xlim(-swath_width / 2, swath_width / 2)
        # Must set ylim after plotting
        mplWidget.canvas.ax.set_ylim(bottom=0, auto=None)
        # Plot it
        mplWidget.canvas.draw()

    def plotCVTable(self, tableWidget: QTableWidget, swath_width: float):
        avg = self._get_average()
        avgPass = PassCardData()
        avgPass.center = self.center
        avgPass.center_method = self.center_method
        a = avgPass.get_data_mod(loc_units=self.swath_units, data=avg)
        # Simulate various Swath Widths, incrimenting by 2 units (-/+) from the center
        for row in range(tableWidget.rowCount()):
            item_sw = tableWidget.item(row, 0)
            item_rt = tableWidget.item(row, 1)
            item_bf = tableWidget.item(row, 2)
            if a.empty:
                item_sw.setText("-")
                item_rt.setText("-")
                item_bf.setText("-")
                continue
            # Print swath width
            _sw = swath_width - (tableWidget.rowCount() - 1) + (2 * row)
            item_sw.setText(f"{_sw} {self.swath_units}")
            # Calc and Print RT CV
            rt_cv = self.calcCV(_sw, False)
            item_rt.setText(f"{rt_cv} %")
            # Calc and Print BF CV
            bf_cv = self.calcCV(_sw, True)
            item_bf.setText(f"{bf_cv} %")

    def calcCV(self, swath_width: float, mirrorAdjascent=False):
        avg = self._get_average()
        avgPass = PassCardData()
        avgPass.center = self.center
        avgPass.center_method = self.center_method
        a = avgPass.get_data_mod(loc_units=self.swath_units, data=avg)
        # Original average data
        x0 = np.array(a["loc"], dtype=float)
        y0 = np.array(a["cov"], dtype=float)
        # create a shifted x array for each simulated pass with labels
        x_arrays = [x0]
        y_arrays = [y0]
        labels = ["Center"]
        for i in range(1, self.simulated_adjascent_passes + 1):
            x = (x0 * -1)[::-1] if mirrorAdjascent and i % 2 != 0 else x0
            y = y0[::-1] if mirrorAdjascent and i % 2 != 0 else y0
            x_arrays.append(x - (i * swath_width))
            y_arrays.append(y)
            labels.append(f"Left {i}")
            x_arrays.append(x + (i * swath_width))
            y_arrays.append(y)
            labels.append(f"Right {i}")
        # Unify the x-domain
        xfill = np.sort(np.concatenate(x_arrays))
        # Interpolate the original y-values to the new x-domain
        y_fills = []
        for i in range(len(x_arrays)):
            y_fills.append(np.interp(xfill, x_arrays[i], y_arrays[i], left=0, right=0))
        # Plot the fills cumulatively in order of generation: C, L1, R1, L2, R2, etc.
        y_fill_cum = np.zeros(xfill.size)
        for i in range(len(y_fills)):
            y_fill_cum = y_fill_cum + y_fills[i]
        # Find average deposition inside swath width
        y_fill_cum_center = y_fill_cum[
            np.where(((xfill >= -swath_width / 2) & (xfill <= swath_width / 2)))
        ]
        return round(variation(y_fill_cum_center, axis=0) * 100)
