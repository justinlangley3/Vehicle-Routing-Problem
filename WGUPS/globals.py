import time

EARTH_SEMI_MAJOR = 6378137.0
EARTH_SEMI_MINOR = 6356752.314245


# Codes for terminal formatting/colors
class Colors:
    # Font Colors
    BLACK = '\33[30m'
    GREY = '\33[90m'
    VIOLET1 = '\33[35m'
    VIOLET2 = '\33[95m'
    BLUE1 = '\33[34m'
    BLUE2 = '\33[94m'
    CYAN1 = '\33[36m'
    CYAN2 = '\33[96m'
    GREEN1 = '\33[32m'
    GREEN2 = '\33[92m'
    YELLOW1 = '\33[33m'
    YELLOW2 = '\33[93m'
    RED1 = '\33[31m'
    RED2 = '\33[91m'
    # Background Colors
    BLACK_BG = "\33[40m"
    GREY_BG = "\33[100m"
    VIOLET1_BG = '\33[45m'
    VIOLET2_BG = '\33[105m'
    BLUE1_BG = '\33[44m'
    BLUE2_BG = '\33[104m'
    CYAN1_BG = '\33[46m'
    CYAN2_BG = '\33[106m'
    GREEN1_BG = '\33[42m'
    GREEN2_BG = '\33[102m'
    YELLOW1_BG = '\33[43m'
    YELLOW2_BG = '\33[103m'
    RED1_BG = '\33[41m'
    RED2_BG = '\33[101m'
    # Special
    END = '\33[0m'
    BOLD = '\33[1m'
    ITALIC = '\33[3m'
    LINE = '\33[4m'
    BLINK1 = '\33[5m'
    BLINK2 = '\33[6m'
    CURSOR = '\33[7m'
