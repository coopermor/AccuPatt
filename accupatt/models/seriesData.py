import uuid
import accupatt.config as cfg
import numpy as np
from accupatt.helpers.atomizationModel import AtomizationModelMulti
from accupatt.models.appInfo import AppInfo
from accupatt.models.passData import Pass
from accupatt.models.seriesCardData import SeriesCardData
from accupatt.models.seriesStringData import SeriesStringData


class SeriesData:
    """A Container class for storing all Series info"""

    def __init__(self, id=""):
        self.id = id
        if self.id == "":
            self.id = str(uuid.uuid4())
        self.info = AppInfo()
        self.passes: list[Pass] = []
        self.string = SeriesStringData(self.passes, self.info.swath_units)
        self.cards = SeriesCardData(self.passes, self.info.swath_units)

    """
    GET methods below optionally take imposed unit, otherwise find most common unit, convert values and return a tuple
    containing (mean_value, mean_value_units, mean_value_and_units_string)
    """

    def get_airspeed_mean(
        self, units=None, string_included=False, cards_included=False
    ) -> tuple[int, str, str]:
        passes = self.get_includable_passes(string_included, cards_included)
        if len(passes) < 1:
            return 0, "-", "-"
        units = (
            units
            if units
            else self._get_common_unit([p.ground_speed_units for p in passes])
        )
        value = round(np.mean([p.get_airspeed(units)[0] for p in passes]))
        return value, units, f"{value} {units}"

    def get_spray_height_mean(
        self, units=None, string_included=False, cards_included=False
    ) -> tuple[float, str, str]:
        passes = self.get_includable_passes(string_included, cards_included)
        if len(passes) < 1:
            return 0, "-", "-"
        units = (
            units
            if units
            else self._get_common_unit([p.spray_height_units for p in passes])
        )
        value = np.mean([p.get_spray_height(units)[0] for p in passes])
        return value, units, f"{value:.1f} {units}"

    def get_wind_speed_mean(
        self, units=None, string_included=False, cards_included=False
    ) -> tuple[float, str, str]:
        passes = self.get_includable_passes(string_included, cards_included)
        if len(passes) < 1:
            return 0, "-", "-"
        units = (
            units
            if units
            else self._get_common_unit([p.wind_speed_units for p in passes])
        )
        value = np.mean([p.get_wind_speed(units)[0] for p in passes])
        return value, units, f"{value:.1f} {units}"

    def get_crosswind_mean(
        self, units=None, string_included=False, cards_included=False
    ) -> tuple[float, str, str]:
        passes = self.get_includable_passes(string_included, cards_included)
        if len(passes) < 1:
            return 0, "-", "-"
        units = (
            units
            if units
            else self._get_common_unit([p.wind_speed_units for p in passes])
        )
        value = np.mean([p.get_crosswind(units)[0] for p in passes])
        return value, units, f"{value:.1f} {units}"

    def get_temperature_mean(
        self, units=None, string_included=False, cards_included=False
    ) -> tuple[float, str, str]:
        passes = self.get_includable_passes(string_included, cards_included)
        if len(passes) < 1:
            return 0, "-", "-"
        units = (
            units
            if units
            else self._get_common_unit([p.temperature_units for p in passes])
        )
        value = np.mean([p.get_temperature(units)[0] for p in passes])
        return value, units, f"{value:.1f} {units}"

    def get_humidity_mean(
        self, string_included=False, cards_included=False
    ) -> tuple[float, str, str]:
        passes = self.get_includable_passes(string_included, cards_included)
        if len(passes) < 1:
            return 0, "-", "-"
        value = np.mean([p.get_humidity()[0] for p in passes])
        return value, "%", f"{value:.1f}%"

    def get_includable_passes(self, string_included, cards_included):
        includablePasses: list[Pass] = []
        for p in self.passes:
            include = True
            if string_included and (
                not p.has_string_data() or not p.string_include_in_composite
            ):
                include = False
            if cards_included and (
                not p.has_card_data() or not p.cards_include_in_composite
            ):
                include = False
            if include:
                includablePasses.append(p)
        return includablePasses

    def _get_common_unit(self, units: list[str]) -> str:
        return max(set(units), key=units.count)

    # Run USDA Model on input params and observables
    def calc_droplet_stats(
        self, string_included=False, cards_included=False
    ) -> tuple[int, int, int, float, float, str, float]:
        model = AtomizationModelMulti()
        for n in self.info.nozzles:
            model.addNozzleSet(
                name=n.type,
                orifice=n.size,
                airspeed=self.get_airspeed_mean(
                    units=cfg.UNIT_MPH,
                    string_included=string_included,
                    cards_included=cards_included,
                )[0],
                pressure=self.info.get_pressure(units=cfg.UNIT_PSI),
                angle=n.deflection,
                quantity=n.quantity,
            )
        return (
            model.dv01(),
            model.dv05(),
            model.dv09(),
            model.p_lt_100(),
            model.p_lt_100(),
            model.dsc(),
            model.rs(),
        )
