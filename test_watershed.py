import copy
import cv2
import time
import matplotlib.pyplot as plt

testfile = "/Users/gill14/Library/Mobile Documents/com~apple~CloudDocs/Projects/AccuPatt/testing/N802EX 01.db"
from accupatt.helpers.dBBridge import load_from_db
from accupatt.models.seriesData import SeriesData
from accupatt.models.sprayCard import SprayCard, SprayCardImageProcessor, SprayCardStats
s = SeriesData()
load_from_db(testfile, s)
sc = s.passes[-1].cards.card_list[2]
sc.watershed = True



# Plot
#figure(figsize=(8, 6), dpi=1200)
#plt.imshow(scip.get_source_mask())
#plt.show()

sc1 = copy.copy(sc)
sc2 = copy.copy(sc)

pre = time.perf_counter()
scip1 = SprayCardImageProcessor(sprayCard=sc1)
#cv2.imshow("old",scip1.draw_and_log_stains()[0])
plt.subplot(1,2,1)
plt.imshow(scip1.draw_and_log_stains()[0])
post = time.perf_counter()
print(f"old in {post-pre:.4f} sec")
pre = time.perf_counter()
scip2 = SprayCardImageProcessor(sprayCard=sc2)
scip2.process_stains()
#cv2.imshow("new",scip2.get_overlay_image())
#plt.imshow(cv2.cvtColor(scip2.get_overlay_image(), cv2.COLOR_BGR2RGB))
plt.subplot(1,2,1)
plt.imshow(scip2.get_mask_image())
plt.subplot(1,2,2)
plt.imshow(scip2.get_overlay_image())
post = time.perf_counter()
print(f"new in {post-pre:.4f} sec")
print(f"Total Stain Count: old = {len(sc1.stain_areas_all_px2)}, new = {len(sc2.stains)}")
print(f"Valid Stain Count: old = {len(sc1.stain_areas_valid_px2)}, new = {len([s for s in sc2.stains if s['is_include']])}")
#waits for user to press any key 
#(this is necessary to avoid Python kernel form crashing)
#cv2.waitKey(0) 
plt.show()
#closing all open windows 
#cv2.destroyAllWindows() 