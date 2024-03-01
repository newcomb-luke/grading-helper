import subprocess
from termcolor import colored, cprint
from interactivity import get_answer_yes_no


def compile_test(path: str, output_file_name: str):
    cprint('---------------------------------------------------------------', 'green')
    cprint(f'Compile test', 'green')
    cprint('---------------------------------------------------------------', 'green')
    try:
        subprocess.run(f'gcc -o ./{output_file_name} {path} -lm', shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def run_test():
    cprint('---------------------------------------------------------------', 'green')
    cprint(f'Interactive test', 'green')
    cprint('---------------------------------------------------------------', 'green')
    try:
        subprocess.run(f'./current-code', shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def hex2dec_test(path: str):
    cprint('---------------------------------------------------------------', 'green')
    cprint('hex2dec program automated test', 'green')
    cprint('---------------------------------------------------------------', 'green')

    tests = [{
                'inputs': ['100F'],
                'answers': ['4111']
        },
             {
                 'inputs': ['BEEF'],
                 'answers': ['48879']
        },
             {
                 'inputs': ['A1', 'CAB', '100F'],
                 'answers': ['161', '3243', '4111']
        },
             {
                 'inputs': ['41', 'DEAD', 'FACC'],
                 'answers': ['65', '57005', '64204']
        },
             {
                 'inputs': ['a1', 'cab', '100f'],
                 'answers': ['161', '3243', '4111']
        },
             {
                 'inputs': ['41', 'dead', 'facc'],
                 'answers': ['65', '57005', '64204']
        },
             {
                 'inputs': ['r2d2'],
                 'answers': ['not']
        },
        ]

    passes = 0
    fails = 0

    for test in tests:
        try:
            hex_numbers = test['inputs']
            answers = test['answers']

            arguments = ' '.join(hex_numbers).strip()

            output = subprocess.getoutput(f'./current-code {arguments}')
            output_answers = output.strip().split('\n')

            if len(answers) != len(output_answers):
                cprint(f'There seems to be a mismatch here. Is {output} correct?', 'yellow')

                if get_answer_yes_no():
                    passes += 1
                else:
                    fails += 1

            for (answer, line) in zip(answers, output_answers):
                if answer in line:
                    passes += 1
                else:
                    cprint(f'Answer {answer} not found, is {line} correct?', 'yellow')

                    if get_answer_yes_no():
                        passes += 1
                    else:
                        fails += 1
        except subprocess.CalledProcessError:
            fails += 1

    return (passes, fails)
