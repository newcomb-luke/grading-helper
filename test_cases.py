import subprocess
from termcolor import colored, cprint


def compile_test(path: str):
    cprint('---------------------------------------------------------------', 'green')
    cprint(f'Compile test', 'green')
    cprint('---------------------------------------------------------------', 'green')
    try:
        subprocess.run(f'gcc -o ./current-executable {path}', shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def run_test(path: str):
    cprint('---------------------------------------------------------------', 'green')
    cprint(f'Interactive test', 'green')
    cprint('---------------------------------------------------------------', 'green')
    try:
        subprocess.run(f'gcc -o ./current-executable {path} && ./current-executable', shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
