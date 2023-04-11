import toml
import subprocess
from interactivity import get_float, get_answer_yes_no
from models import Student, Name, LoadedDir, Grade, to_dict, Submission
from test_cases import compile_test, run_test, calc_test
from termcolor import colored, cprint
import json
import os


def files_to_submissions(submission_files: list[os.DirEntry], students: dict[str, Student]):
    pre_submissions = {}

    if len(submission_files) == 0:
        print("No assignments in folder")
        return []

    for f in submission_files:

        split_name = iter(f.name.split('_'))
        student_name = next(split_name)
        is_late = False

        maybe_late = next(split_name)
        if maybe_late == 'LATE':
            is_late = True
            student_id = int(next(split_name))
        else:
            student_id = int(maybe_late)

        student = students[student_name]

        if student is None:
            print(f'Student of Canvas name {student_name} was not in students.txt')
            exit(1)

        if pre_submissions[student_name] is None:
            pre_submissions[student_name] = {
                        "calc": None,
                        "shell": None,
                        "student_id": student_id,
                        "is_late": is_late,
                        "student": student
                    }

        if "calc" in f.name:
            if pre_submissions[student_name]["calc"] is None:
                print(f"Two calc files submitted by student {student_name}")
                exit(1)

            pre_submissions[student_name]["calc"] = f
        else:
            if pre_submissions[student_name]["shell"] is None:
                print(f"Two shell files submitted by student {student_name}")
                exit(1)

            pre_submissions[student_name]["shell"] = f

    submissions = []

    for name, data in pre_submissions:
        student = data["student"]
        student_id = data["student_id"]
        is_late = data["is_late"]
        shell_file = data["shell"]
        calc_file = data["calc"]

        submissions.append(Submission(shell_file, calc_file, student, student_id, is_late))

    return submissions


def head_file(path: os.DirEntry, num_lines: int) -> str:
    s = ''

    with open(path.path, 'r') as f:
        for i in range(num_lines):
            s += f'{f.readline()}\n'

    return s


def read_file_contents(path: os.DirEntry) -> str:
    s = ''

    with open(path.path, 'r') as f:
        for line in f.readlines():
            s += f'{line}\n'

    return s


def review_code_file(file, extension, output_file_name: str):
    extension_whitelist = ['c']

    cprint('===============================================================', 'green')
    cprint(f'Submission file name: {file.name}', 'green')
    cprint(f'Submission file extension: {extension}', 'green')
    cprint('===============================================================', 'green')

    should_print_contents = True
    extension_in_whitelist = extension in extension_whitelist

    if not extension_in_whitelist:
        cprint('Extension not in whitelist, view file contents?', 'red')
        should_print_contents = get_answer_yes_no()

    if should_print_contents:
        cprint('File contents: ', 'green')
        cprint('---------------------------------------------------------------', 'green')

        cprint(read_file_contents(file), 'yellow')

    cprint('---------------------------------------------------------------', 'green')

    if extension_in_whitelist:
        cprint('Attempting compilation...', 'green')
    else:
        cprint('Skipping compilation due to unrecognized file extension...', 'red')

    subprocess.run(f'dos2unix {file.path}', check=True, shell=True)

    if not compile_test(file.path, output_file_name):
        cprint('Compiling failed!', 'red')
        return False

    return True


def grade_submission(submission: Submission) -> Grade:
    extension_whitelist = ['c']

    cprint('===============================================================', 'green')
    cprint(f'Student name: {submission.student.name}', 'green')
    cprint(f'Late: {"Yes" if submission.is_late else "No"}', 'green')
    cprint('===============================================================', 'green')

    calc_worked = review_code_file(submission.calc_file, submission.extensions()[1], "calc")
    shell_worked = review_code_file(submission.shell_file, submission.extensions()[0], "current-executable")

    if not shell_worked and not calc_worked:
        cprint('Neither succeeded to compile, auto 19?', 'red')

        if get_answer_yes_no():
            cprint('Leave a comment?', 'yellow')

            comment = None

            if get_answer_yes_no():
                comment = input('> ')

            return Grade(submission, 19.0, comment=comment)

    running_grade = 0.0

    if calc_worked:
        cprint('calc compiled successfully, running calc tests', 'green')

        passes, fails = calc_test(submission.calc_file)

        cprint('===============================================================', 'green')
        cprint(f'Passes: {passes}', 'green')
        cprint(f'Fails: {fails}', 'yellow')
        cprint('===============================================================', 'green')

        running_grade += passes * 5.0

    if not shell_worked:
        cprint('Shell failed to compile.', 'red')

        if not calc_worked:
            cprint('Calc failed to compile.', 'red')
        else:
            running_grade += 25.0

        cprint(f'Use partial grade of {running_grade}?', 'yellow')

        grade = 0.0

        if get_answer_yes_no():
            grade = running_grade
        else:
            cprint('Score: ', 'green')
            grade = get_float()

        cprint('Comment:', 'green')

        comment = input('> ')

        if len(comment.strip()) == 0:
            comment = None

        return Grade(submission, grade, comment)

    if shell_worked and not calc_worked:
        cprint('Calc failed to compile. Using reference implementation.', 'red')
        # Use reference calc implementation
        subprocess.run("gcc -o calc reference-calc.c", shell=True, check=True)

    cprint('Should attempt to run?', 'green')

    should_run = get_answer_yes_no()

    while should_run:
        try:
            if not run_test(submission.file.path):
                cprint('Program crashed!', 'red')
        except KeyboardInterrupt:
            cprint('\nProgram exited by you', 'yellow')

        cprint('Run again?', 'green')

        should_run = get_answer_yes_no()

    cprint('Score: ', 'green')

    score = get_float()

    cprint('Leave a comment?', 'green')
    comment = None

    if get_answer_yes_no():
        comment = input('> ')

    return Grade(submission, score, comment=comment)


def load_from_disk(students_map):
    submission_files = []

    for file in os.scandir(ASSIGNMENTS_FOLDER):
        if not file.name.startswith("."):
            submission_files.append(file)

    submission_files.sort(key=lambda x: x.name)

    return files_to_submissions(submission_files, students_map)


def load_from_backup():
    with open('grades-backup.json', 'r') as f:
        data = json.load(f)

        grades = [Grade.from_dict(x) for x in data['grades']]

        remaining_submissions = [Submission.from_dict(x) for x in data['ungraded']]

        return remaining_submissions, grades


if __name__ == '__main__':
    ASSIGNMENTS_FOLDER = 'assignments'

    students = []
    students_map = {}

    with open('students.txt', 'r') as f:
        for line in f.readlines():
            student = Student(Name.from_str(line))
            students.append(student)
            students_map[student.name.to_canvas()] = student

    submissions = []
    grades = []

    if os.path.exists('grades-backup.json'):
        print('Existing grades backup detected')
        print('Should it be loaded?')

        if get_answer_yes_no():
            submissions, grades = load_from_backup()
        else:
            submissions = load_from_disk(students_map)
    else:
        submissions = load_from_disk(students_map)

    for i in range(len(submissions)):
        submission = submissions[i]
        grades.append(grade_submission(submission))

        with open('grades-backup.json', 'w') as f:
            data = {
                'grades': [to_dict(grade) for grade in grades],
                'ungraded': [to_dict(x) for x in submissions[i + 1:]]
            }

            json.dump(data, f, indent=4)

        cprint('Keep grading?', 'green')
        if not get_answer_yes_no():
            break

    grades_map = {'grades': []}

    for grade in grades:
        entry = {
            'student': str(grade.submission.student.name),
            'score': grade.score,
        }

        if grade.comment is not None:
            entry['comment'] = grade.comment

        grades_map['grades'].append(entry)

    with open('grades.toml', 'w') as f:
        toml.dump(grades_map, f)
