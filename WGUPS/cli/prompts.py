# Project Imports
from .style import Style


def display_welcome():
    pad = ' '
    line_fill = '+' + ('-' * 68) + '+'

    title = 'WGUPS Package Routing & Delivery'
    title_margin = pad * (((70 - len(title)) // 2) - 1)

    exit_help = f'Press {Style.RED2}{Style.UNDERLINE}Ctrl-C{Style.END} at any time to exit.'
    exit_margin = pad * ((85 - len(exit_help)) // 2)

    welcome_text = f'{Style.GREY}{line_fill}{Style.END}\n' \
                   f'{Style.GREY}|{Style.END}{title_margin}{Style.BLUE1}{title}{Style.END}{Style.GREY}{title_margin}|{Style.END}\n' \
                   f'{Style.GREY}{line_fill}{Style.END}\n' \
                   f'{exit_margin}{exit_help}{exit_margin}\n' \
                   f'\n{Style.GREY}{line_fill}{Style.END}\n'

    info = f'Please take a moment to import your data files.\n' \
           f'Press <{Style.YELLOW2}{Style.RED2}ENTER{Style.END}> to continue ...' \
           f'\n{Style.GREEN1}>{Style.END}'

    welcome_text += info
    input(welcome_text)


def cmd_help(arg: str):
    text = ''
    match arg:
        case 'l':
            text = f'Usage:\n' \
                   f'-l [option] [value]\n' \
                   f'-------------------' \
                   f'Option\t|\tValue\n' \
                   f'--------------------\n' \
                   f'a, lookup package by ADDRESS\n' \
                   f'd, lookup package by DEADLINE\n' \
                   f'c, lookup package by CITY\n' \
                   f'i, lookup package by ID\n' \
                   f's, lookup package by STATUS\n' \
                   f'w, lookup package by WEIGHT\n' \
                   f'z, lookup package by ZIP'
        case 'la':
            text = f'Usage:\n' \
                   f'-la [value], lookup package by ADDRESS\n' \
                   f'Description:\n' \
                   f'The value parameter must exactly match the street address of the package.'
        case 'ld':
            text = f'Usage:\n' \
                   f'-ld [value], lookup package by DEADLINE\n' \
                   f'Description:\n' \
                   f'The value must be a valid time in 24hr format [HH:MM] e.g. 09:59 or 21:59.'
        case 'lc':
            text = f'Usage:\n' \
                   f'-lc [value], lookup package by CITY\n' \
                   f'Description:\n' \
                   f'The value must exactly match the city of the package.'
        case 'li':
            text = f'Usage:\n' \
                   f'-li [value], lookup package by ID\n' \
                   f'Description:\n' \
                   f'The value must be a valid integer ID of the package.'
        case 'ls':
            text = f'Usage:\n' \
                   f'-ls [value], lookup package by STATUS\n' \
                   f'Description:\n' \
                   f'The value must match a valid status: \'hub\', \'enroute\', \'delivered\'.'
        case 'lw':
            text = f'Usage:\n' \
                   f'-lw [value], lookup package by WEIGHT\n' \
                   f'Description:\n' \
                   f'The value must be a valid integer value.'
        case 'lz':
            text = f'Usage:\n' \
                   f'-lz [value], lookup package by ZIP\n' \
                   f'Description:\n' \
                   f'The value must be a valid 5-digit zipcode.'
        case 's':
            text = f'Usage:\n' \
                   f'-s[option], simulate delivery of currently loaded trucks' \
                   f'Description:\n' \
                   f'Simulates delivery using the specified algorithm option.\n' \
                   f'If no option is chosen, convex hull is used by default.' \
                   f'Options:\n' \
                   f'a - ant colony optimization (metaheuristic)\n' \
                   f'c - convex hull\n' \
                   f'g - genetic algorithm (metaheuristic)\n' \
                   f'n - nearest neighbor'
        case 'm':
            text = f'Usage:\n' \
                   f'-m' \
                   f'Description:' \
                   f'Displays metrics of any present trucks if delivery has been simulated.'
        case 'u':
            text = f'Usage:\n' \
                   f'-u[option] [value]\n' \
                   f'Description:\n' \
                   f'Update a package parameter to the specified value.\n' \
                   f'Options:\n' \
                   f'a, address\n' \
                   f'd, deadline\n' \
                   f'c, city\n' \
                   f'w, weight\n' \
                   f'z, zip'
        case '_':
            text = 'Invalid argument provided'
    print(text)


def choose_int(prompt: str, count: int) -> int:
    """
    Present the user with a prompt and have them make a selection
    The selection must be an integer value between 0 and the value of options inclusive

    The prompt should include text representations of all valid choices
    """
    from re import compile, match
    pattern = compile("^[0-9]$")

    is_file_selected = False
    while not is_file_selected:
        from .environment import cls
        cls()
        choice = input(prompt)
        try:
            assert match(pattern, choice)
            assert 0 <= int(choice) <= count
            is_file_selected = True
            return int(choice)
        except AssertionError:
            print(f'{Style.RED1}Input must be a value shown{Style.END}', flush=True)
            input(f'Press {Style.YELLOW2}ENTER{Style.END} to retry ...')
            pass
