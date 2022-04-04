class Style:
    """
    The values represented here are ANSI codes for various command-line styling.
    Note: These are not all the ANSI codes that may be used, but a handful of them

    These values can be inserted in 'f-strings' to add style to text
    Color values can be combined with other values like bold, italic, underline

    There are two special 'control' values:
      END - Clears any styling:
            + Reverts to white on black with no applied styles

      CLS - Clears output:
            Uses two sequences that accomplish the following,
            + Scrolls cursor to the beginning of any present output
            + Clears from the cursor to end of the output

    Example Usage:
      Style:
      - f'{TColor.STYLE}Text to format{TColor.END}'

      Color:
      - f'{TColor.VALUE}Text to format{TColor.END}'

      Color + Style
      - f'{TColor.VALUE}{TColor.STYLE}Text to format{TColor.END}'
    """
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
    BOLD = '\33[1m'
    ITALIC = '\33[3m'
    UNDERLINE = '\33[4m'
    BLINK1 = '\33[5m'
    BLINK2 = '\33[6m'
    CURSOR = '\33[7m'
    # Control
    CLS = '\033[H\033[J'
    END = '\33[0m'
