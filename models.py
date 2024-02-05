import os


def to_dict(o):
    return o.__to_dict__()


class Name:
    def __init__(self, first: str, last: str):
        self.first = first
        self.last = last

    @staticmethod
    def from_str(s: str):
        split = s.split(' ')
        first_name = split[0]
        last_name = ''

        for i in range(1, len(split)):
            last_name += split[i]

        return Name(first_name, last_name.rstrip())

    def to_canvas(self) -> str:
        canvas = ''

        for c in self.last:
            if c.isalpha():
                canvas += c

        canvas += self.first

        return canvas.lower()

    def __str__(self):
        return f'{self.first} {self.last}'

    def __repr__(self):
        return str(self)

    def __to_dict__(self):
        return {'first': self.first, 'last': self.last}

    @staticmethod
    def from_dict(d):
        return Name(d['first'], d['last'])


class Student:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return str(self)

    def __to_dict__(self):
        return {'name': to_dict(self.name)}

    @staticmethod
    def from_dict(d):
        return Student(Name.from_dict(d['name']))


def file_extension(file: os.DirEntry) -> str | None:
    if file is None:
        return None

    return file.name.split('.')[-1]


class Submission:
    def __init__(self, code_file: os.DirEntry, student: Student, student_id: int, is_late: bool):
        self.code_file = code_file
        self.student = student
        self.student_id = student_id
        self.is_late = is_late

    def extensions(self) -> tuple[str | None]:
        return (file_extension(self.code_file),)

    def __to_dict__(self):
        return {
            'code_file': self.code_file.path if self.code_file is not None else None,
            'student': to_dict(self.student),
            'student_id': self.student_id,
            'is_late': self.is_late
        }

    @staticmethod
    def from_dict(d):
        return Submission(
            LoadedDir.from_path(d['code_file']),
            Student.from_dict(d['student']),
            d['student_id'],
            d['is_late']
        )


class Grade:
    def __init__(self, submission: Submission, score: float, comment: str = None):
        self.submission = submission
        self.score = score
        self.comment = comment

    def __to_dict__(self):
        return {
            'submission': to_dict(self.submission),
            'score': self.score,
            'comment': self.comment
        }

    @staticmethod
    def from_dict(d):
        return Grade(
            Submission.from_dict(d['submission']),
            d['score'],
            comment=d['comment']
        )


class LoadedDir:
    def __init__(self, path, name):
        self.path = path
        self.name = name

    @staticmethod
    def from_path(path: str | None):

        if path is None:
            return None

        name = path.split(os.sep)[-1]
        return LoadedDir(path, name)
