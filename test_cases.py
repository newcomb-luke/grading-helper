import subprocess
from termcolor import colored, cprint
from interactivity import get_answer_yes_no


def compile_test(path: str, output_file_name: str):
    cprint('---------------------------------------------------------------', 'green')
    cprint(f'Compile test', 'green')
    cprint('---------------------------------------------------------------', 'green')
    try:
        subprocess.run(f'gcc -o ./{output_file_name} {path}', shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def run_test(path: str):
    cprint('---------------------------------------------------------------', 'green')
    cprint(f'Interactive test', 'green')
    cprint('---------------------------------------------------------------', 'green')

    args = input("Command line arguments to pass: ")

    try:
        subprocess.run(f'./current-executable {args}', shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
