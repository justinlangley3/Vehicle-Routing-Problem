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
                   f'{Style.GREY}|{Style.END}{title_margin}' \
                   f'{Style.BLUE1}{title}{Style.END}' \
                   f'{Style.GREY}{title_margin}|{Style.END}\n' \
                   f'{Style.GREY}{line_fill}{Style.END}\n' \
                   f'{exit_margin}{exit_help}{exit_margin}\n' \
                   f'\n{Style.GREY}{line_fill}{Style.END}\n'

    info = f'Please take a moment to import your data files.\n' \
           f'Press <{Style.YELLOW2}{Style.RED2}ENTER{Style.END}> to continue ...' \
           f'\n{Style.GREEN1}>{Style.END}'

    welcome_text += info
    input(welcome_text)


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
            input(f'Press <{Style.YELLOW2}ENTER{Style.END}> to retry ...')
            pass
