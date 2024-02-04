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
    try:
        subprocess.run(f'./current-executable', shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def calc_test(path: str):
    cprint('---------------------------------------------------------------', 'green')
    cprint('Calc program automated test', 'green')
    cprint('---------------------------------------------------------------', 'green')

    tests = [{
                'num1': 5,
                'operator': "*",
                'num2': 7,
                'answer': 35
        },
             {
                'num1': 60,
                'operator': "-",
                'num2': 27,
                'answer': 60 - 27
        },
             {
                'num1': 814,
                'operator': "/",
                'num2': 11,
                'answer': 74
        },
             {
                 'num1': 77798,
                 'operator': "+",
                 'num2': 2,
                 'answer': 77800
        }]

    passes = 0
    fails = 0

    for test in tests:
        try:
            num1 = test['num1']
            num2 = test['num2']
            operator = test['operator']
            answer = test['answer']

            output = subprocess.getoutput(f'./calc {num1} "{operator}" {num2}')
            output = output.strip()

            epsilon = 0.0001

            found = False

            for token in output.split():
                parsed = True
                parse_output = 0.0

                try:
                    parse_output = float(token)
                except ValueError:
                    parsed = False

                if parsed and answer + epsilon > parse_output and answer - epsilon < parse_output:
                    found = True
                    break

            if found:
                passes += 1
            else:
                cprint(f'Answer {answer} not found, is {output} correct?', 'yellow')

                if get_answer_yes_no():
                    passes += 1
                else:
                    fails += 1
        except subprocess.CalledProcessError:
            fails += 1

    try:
        error_output = subprocess.getoutput(f'./calc chewsday')

        cprint(f'Error output: "{error_output}"', 'green')
        cprint('Is this valid?', 'green')

        if get_answer_yes_no():
            passes += 1
        else:
            fails += 1

    except subprocess.CalledProcessError:
        fails += 1

    return (passes, fails)
