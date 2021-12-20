#Unit Labels
UNIT_MPH = 'mph'
UNIT_KPH = 'kph'
UNIT_FT = 'ft'
UNIT_M = 'm'
UNIT_DEG_F = '°F'
UNIT_DEG_C = '°C'

#Unit Option Lists
UNITS_LENGTH_LARGE = [UNIT_FT, UNIT_M]
UNITS_GS = [UNIT_MPH, UNIT_KPH]
UNITS_SH = [UNIT_FT, UNIT_M]
UNITS_WS = [UNIT_MPH, UNIT_KPH]
UNITS_T = [UNIT_DEG_F, UNIT_DEG_C]

# Math Conversion Constants
UM_PER_IN = 25400.0
FT_PER_M = 3.28084
MPH_PER_KPH = 0.621371
MPH_PER_KN = 1.15078

# String Drive Commands
STRING_DRIVE_FWD_START = 'AD+\r'
STRING_DRIVE_FWD_STOP = 'AD\r'
STRING_DRIVE_REV_START = 'BD-\r'
STRING_DRIVE_REV_STOP = 'BD\r'

# SprayCard Inclusion Constants
HAS_IMAGE_NO = 0
HAS_IMAGE_NO_STRING = 'No'
HAS_IMAGE_YES = 1
HAS_IMAGE_YES_STRING = 'Yes'
INCLUDE_IN_COMPOSITE_NO = 0
INCLUDE_IN_COMPOSITE_NO_STRING = 'Exclude'
INCLUDE_IN_COMPOSITE_YES = 1
INCLUDE_IN_COMPOSITE_YES_STRING = 'Include'

# SprayCard Thresholding Constants
THRESHOLD_TYPE__DEFAULT = 0
THRESHOLD_TYPE_GRAYSCALE = 0
THRESHOLD_TYPE_GRAYSCALE_STRING = 'Grayscale'
THRESHOLD_TYPE_COLOR = 1
THRESHOLD_TYPE_COLOR_STRING = 'Color'
# SprayCard Thresholding Constants (Grayscale)
THRESHOLD_GRAYSCALE__DEFAULT = 152
THRESHOLD_METHOD_GRAYSCALE__DEFAULT = 0
THRESHOLD_METHOD_AUTOMATIC = 0
THRESHOLD_METHOD_AUTOMATIC_STRING = 'Auto'
THRESHOLD_METHOD_MANUAL = 1
THRESHOLD_METHOD_MANUAL_STRING = 'Manual'
# SprayCard Thresholding Constants (Color)
THRESHOLD_COLOR_HUE__DEFAULT = (180,240)
THRESHOLD_COLOR_SATURATION__DEFAULT = (6,255)
THRESHOLD_COLOR_BRIGHTNESS__DEFAULT = (0,255)
THRESHOLD_METHOD_COLOR__DEFAULT = 0
THRESHOLD_METHOD_INCLUDE = 0
THRESHOLD_METHOD_INCLUDE_STRING = 'Include'
THRESHOLD_METHOD_EXCLUDE = 1
THRESHOLD_METHOD_EXCLUDE_STRING = 'Exclude'

# SprayCard Processed Image Colors
COLOR_STAIN_OUTLINE = (138, 43, 226) #Red-Pink
COLOR_STAIN_FILL_ALL = (0, 0, 255) #Red
COLOR_STAIN_FILL_VALID = (255, 0, 0) #Blue

# SprayCard Spread Factor Methods
SPREAD_FACTOR_A__DEFAULT = 0.0000
SPREAD_FACTOR_B__DEFAULT = 0.0009
SPREAD_FACTOR_C__DEFAULT = 1.6333
SPREAD_METHOD__DEFAULT = 2
SPREAD_METHOD_NONE = 0
SPREAD_METHOD_NONE_STRING = 'None'
SPREAD_METHOD_DIRECT = 1
SPREAD_METHOD_DIRECT_STRING = 'Direct'
SPREAD_METHOD_ADAPTIVE = 2
SPREAD_METHOD_ADAPTIVE_STRING = 'Adaptive'
    
