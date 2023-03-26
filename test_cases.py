import subprocess
from termcolor import colored, cprint


def run_with_interactive(path: str, choice: int):
    cprint('---------------------------------------------------------------', 'green')
    cprint(f'Interactive test for input: {choice}', 'green')
    cprint('---------------------------------------------------------------', 'green')
    try:
        subprocess.run(f'bash {path}', shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def run_with_argument(path: str, choice: int):
    cprint('---------------------------------------------------------------', 'green')
    cprint(f'Argument test for input: {choice}', 'green')
    cprint('---------------------------------------------------------------', 'green')
    try:
        subprocess.run(f'bash {path} {choice}', shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
