import toml
import subprocess
from interactivity import *
from models import *
from test_cases import compile_test, run_test
from termcolor import colored, cprint
import json


def files_to_submissions(submission_files: list[os.DirEntry], students: dict[str, Student]):
    submissions = []

    if len(submission_files) == 0:
        print("No assignments in folder")
        return submissions

    for f in submission_files:

        print(f"{f.name}")

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
            exit(f'Student of Canvas name {student_name} was not in students.txt')

        submissions.append(Submission(f, student, student_id, is_late))

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


def grade_submission(submission: Submission) -> Grade:
    extension_whitelist = ['c']

    cprint('===============================================================', 'green')
    cprint(f'Student name: {submission.student.name}', 'green')
    cprint(f'Late: {"Yes" if submission.is_late else "No"}', 'green')
    cprint(f'Submission file extension: {submission.extension()}', 'green')
    cprint('===============================================================', 'green')

    should_print_contents = True

    if submission.extension() not in extension_whitelist:
        cprint('Extension not in whitelist, view file contents?', 'red')
        should_print_contents = get_answer_yes_no()

        cprint('Auto 19?', 'red')
        if get_answer_yes_no():

            cprint('Leave a comment?', 'red')
            comment = None

            if get_answer_yes_no():
                comment = input('> ')

            return Grade(submission, 19.0, comment=comment)

    if should_print_contents:
        cprint('File contents: ', 'green')
        cprint('---------------------------------------------------------------', 'green')

        cprint(read_file_contents(submission.file), 'yellow')

    cprint('---------------------------------------------------------------', 'green')

    cprint('Compile?', 'green')

    if get_answer_yes_no():
        subprocess.run(f'dos2unix {submission.file.path}', check=True, shell=True)

        if not compile_test(submission.file.path):
            cprint('Compiling failed!', 'red')

            cprint('Auto 19?', 'red')

            if get_answer_yes_no():
                cprint('Leave a comment?', 'red')
                comment = None

                if get_answer_yes_no():
                    comment = input('> ')

                return Grade(submission, 19.0, comment=comment)

    if os.path.exists("studentData.bin"):
        os.remove("studentData.bin")

    cprint('Should attempt to run?', 'green')

    should_run = get_answer_yes_no()

    while should_run:
        subprocess.run(f'dos2unix {submission.file.path}', check=True, shell=True)

        try:
            if not run_test(submission.file.path):
                cprint('Program crashed!', 'red')
        except KeyboardInterrupt:
            cprint('\nProgram exited by you', 'yellow')

        cprint('Run again?', 'green')

        should_run = get_answer_yes_no()

    if os.path.exists("studentData.bin"):
        os.remove("studentData.bin")

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
