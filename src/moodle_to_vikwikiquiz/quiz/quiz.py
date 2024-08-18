import contextlib

# future: report false positive to JetBrains developers
# noinspection PyUnresolvedReferences
import os

# noinspection PyUnresolvedReferences
from pathlib import Path

# noinspection PyUnresolvedReferences
import re
import shutil
from urllib.parse import unquote

# noinspection PyUnresolvedReferences
from bs4 import BeautifulSoup, Tag

# noinspection PyPackages
from .questions.answer import Answer  # type: ignore

# noinspection PyPackages
# future: report false positive to mypy developers
from .grading_types import GradingType  # type: ignore

# noinspection PyPackages
from .illustrations.illustration import Illustration  # type: ignore

# noinspection PyPackages
from .illustrations.state_of_illustrations import StateOfIllustrations  # type: ignore

# noinspection PyPackages
from .questions.question_types import QuestionType  # type: ignore

# noinspection PyPackages
from .quiz_helpers import *  # type: ignore

# noinspection PyPackages
from .questions.question import Question  # type: ignore

# noinspection PyPackages
from .quiz_element import QuizElement  # type: ignore


def move_illustration_to_upload_folder(
    quiz_element: QuizElement, upload_directory: str
) -> None:
    if illustration := quiz_element.illustration:
        if not os.path.exists(upload_directory):
            os.makedirs(upload_directory)
        original_file_path = illustration.original_file_path.resolve()
        original_file_path = unquote(str(original_file_path))
        shutil.copy(original_file_path, upload_directory)
        current_file_path = Path(
            os.path.join(upload_directory, illustration.original_file_path.name)
        )
        new_file_path = os.path.join(
            current_file_path.parent, illustration.upload_filename
        )
        os.rename(current_file_path, new_file_path)


class Quiz:
    def __init__(
        self, parent_article: str, title: str, grading: GradingType | None = None
    ):
        self.parent_article = parent_article
        self.title = title
        self.grading = grading

        self.questions: set[Question] = set()
        self.state_of_illustrations = StateOfIllustrations.Nil

    def __str__(self) -> str:
        text = f"{{{{Vissza | {self.parent_article}}}}}"
        text += f"""{{{{Kvízoldal
| cím = {self.title}"""
        if self.grading:
            text += f"\n| pontozás = {self.grading.value}"
        text += "\n}}"
        for question in self.questions:
            text += f"\n\n\n{question}"
        text += "\n"
        return text

    def import_file_or_files(self, path: Path, recursively: bool) -> None:
        if os.path.isfile(path):
            self.import_questions(path, path.parent)
        else:
            self.import_files(path, recursively)
        if not self.questions:
            raise ValueError(f"No questions were imported from '{path}'!")

    def import_files(self, path: Path, recursively: bool) -> None:
        for subdir, dirs, files in os.walk(path):
            for file in files:
                self.import_questions(file, subdir)
            if not recursively:
                break

    def import_questions(self, file: Path | str, subdir: Path | str) -> None:
        file_path = os.path.join(subdir, file)
        with open(file_path, "rb") as source_file:
            webpage = BeautifulSoup(source_file, "html.parser")

            multi_or_single_choice_questions = webpage.find_all(
                "div", class_=re.compile(r"multichoice|calculatedmulti|truefalse")
            )
            for question in multi_or_single_choice_questions:
                self.import_question(question, file_path, subdir, file)
                clear_terminal()  # type: ignore

    def import_question(
        self, question: Tag, file_path: str, subdir: Path | str, file: Path | str
    ) -> None:
        if self.state_of_illustrations == StateOfIllustrations.Nil:
            self.state_of_illustrations = get_if_has_illustration(question, subdir, file)  # type: ignore
        with contextlib.suppress(NotImplementedError):
            question_type = get_question_type(question)  # type: ignore
        correctly_answered, grade, maximum_points = get_grading_of_question(question)  # type: ignore
        question_text, illustration = get_question_data(question, self.title, Question, self.state_of_illustrations)  # type: ignore
        answers, id_of_correct_answers, all_correct_answers_known = self.get_answers(  # type: ignore
            question, grade, maximum_points
        )
        if not correctly_answered and not all_correct_answers_known:
            complete_correct_answers(  # type: ignore
                answers,
                id_of_correct_answers,
                grade,
                maximum_points,
                question_text,
                question_type,
                os.path.basename(file_path),
            )
        self.add_question_no_duplicates(
            question_type,
            question_text,
            self.state_of_illustrations,
            illustration,
            answers,
            id_of_correct_answers,
        )

    def get_answers(
        self, question: Tag, grade: float, maximum_points: float
    ) -> tuple[list[Answer], set[int], bool]:
        answers = question.find("div", class_="answer")
        correct_answers = get_correct_answers_if_provided(question)  # type: ignore
        all_correct_answers_known = bool(correct_answers)
        assert isinstance(answers, Tag)
        answers_to_add: list[Answer] = []
        illustration: Illustration | None = None
        id_of_correct_answers: set[int] = set()
        i = 1
        for answer in answers:
            if not isinstance(answer, Tag):
                continue
            found_tag = answer.find(class_="ml-1")
            assert isinstance(found_tag, Tag)
            if found_tag.find(class_="MathJax"):
                answer_text = format_latex_as_wikitext(found_tag)  # type: ignore
            else:
                match answer_text := found_tag.text:
                    case "True":
                        answer_text = "Igaz"
                    case "False":
                        answer_text = "Hamis"
                    case _:
                        answer_text = prettify(answer_text)  # type: ignore
            if found_tag.find("img"):
                illustration = get_element_illustration(found_tag, answer_text, self.title, Answer, self.state_of_illustrations)  # type: ignore
            answers_to_add.append(Answer(answer_text, illustration))
            if answer_is_correct(  # type: ignore
                answer, answer_text, grade, maximum_points, correct_answers
            ):
                id_of_correct_answers.add(i)
            i += 1
        return answers_to_add, id_of_correct_answers, all_correct_answers_known

    def add_question_no_duplicates(
        self,
        question_type: QuestionType,
        question_text: str,
        has_illustration: StateOfIllustrations,
        illustration: Illustration | None,
        answers: list[Answer],
        correct_answers: set[int],
    ) -> None:
        for existing_question in self.questions:
            if question_already_exists(existing_question, question_text):  # type: ignore
                add_answers_to_existing_question(  # type: ignore
                    answers, correct_answers, existing_question
                )
                break
        else:
            self.add_question(
                answers,
                correct_answers,
                has_illustration,
                illustration,
                question_text,
                question_type,
            )

    def add_question(
        self,
        answers: list[Answer],
        correct_answers: set[int],
        has_illustration: StateOfIllustrations,
        illustration: Illustration | None,
        question_text: str,
        question_type: QuestionType,
    ) -> None:
        try:
            self.questions.add(
                Question(
                    q_type=question_type,
                    text=question_text,
                    state_of_illustrations=has_illustration,
                    answers=answers,
                    correct_answers=correct_answers,
                    illustration=illustration,
                )
            )
        except AssertionError:
            print(
                f"Error: question '{question_text}' was not added to the quiz because it wasn't processed correctly!"
            )

    def get_illustrations_ready_for_upload(self) -> None:
        upload_directory = os.path.join(os.getcwd(), "to_upload")
        for question in self.questions:
            move_illustration_to_upload_folder(question, upload_directory)
            for answer in question.answers:
                if answer.illustration:
                    move_illustration_to_upload_folder(answer, upload_directory)
