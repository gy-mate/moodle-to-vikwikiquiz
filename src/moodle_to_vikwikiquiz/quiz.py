import contextlib

# future: report false positive to JetBrains developers
# noinspection PyUnresolvedReferences
import os

# future: report false positive to JetBrains developers
# noinspection PyUnresolvedReferences
from bs4 import BeautifulSoup, Tag

# future: report false positive to JetBrains developers
# noinspection PyPackages
# future: report false positive to mypy developers
from .grading_types import GradingType  # type: ignore

# noinspection PyPackages
# future: report false positive to mypy developers
from .question_types import QuestionType  # type: ignore

# noinspection PyPackages
# future: report false positive to mypy developers
from .quiz_helpers import *  # type: ignore

# noinspection PyPackages
# future: report false positive to mypy developers
from .question import Question  # type: ignore


class Quiz:
    def __init__(
        self, parent_article: str, title: str, grading: GradingType | None = None
    ):
        self.parent_article = parent_article
        self.title = title
        self.grading = grading

        self.questions: set[Question] = set()

    def __str__(self) -> str:
        text = f"{{{{Vissza | {self.parent_article}}}}}"
        text += f"""

{{{{Kvízoldal
|cím={self.title}"""
        if self.grading:
            text += f"\n|pontozás={self.grading.value}"
        text += "\n}}"
        for question in self.questions:
            text += f"\n\n\n{question}"
        text += "\n"
        return text

    def import_files(self, directory: str) -> None:
        for subdir, dirs, files in os.walk(directory):
            for file in files:
                self.import_questions(file, subdir)

    def import_questions(self, file: str, subdir: str) -> None:
        file_path = os.path.join(subdir, file)
        with open(file_path, "rb") as source_file:
            webpage = BeautifulSoup(source_file, "html.parser")

            multi_or_single_choice_questions = webpage.find_all(
                "div", class_="multichoice"
            )
            for question in multi_or_single_choice_questions:
                self.import_question(
                    question=question, file_name=os.path.basename(file_path)
                )
                clear_terminal()  # type: ignore

    def import_question(self, question: Tag, file_name: str) -> None:
        with contextlib.suppress(NotImplementedError):
            question_type = get_question_type(question)  # type: ignore
        correctly_answered, grade, maximum_points = get_grading_of_question(question)  # type: ignore
        question_text = get_question_text(question)  # type: ignore
        answer_texts, correct_answers = get_answers(question, grade, maximum_points)  # type: ignore
        if not correctly_answered:
            complete_correct_answers(  # type: ignore
                answer_texts,
                correct_answers,
                grade,
                maximum_points,
                question_text,
                question_type,
                file_name,
            )
        has_illustration = get_if_has_illustration(question)  # type: ignore
        self.add_question_no_duplicates(
            question_type,
            question_text,
            has_illustration,
            answer_texts,
            correct_answers,
        )

    def add_question_no_duplicates(
        self,
        question_type: QuestionType,
        question_text: str,
        has_illustration: bool,
        answer_texts: list[str],
        correct_answers: list[int],
    ) -> None:
        for existing_question in self.questions:
            if question_already_exists(existing_question, question_text):  # type: ignore
                add_answers_to_existing_question(  # type: ignore
                    answer_texts, correct_answers, existing_question
                )
                break
        else:
            self.questions.add(
                Question(
                    q_type=question_type,
                    text=question_text,
                    illustration=has_illustration,
                    answers=answer_texts,
                    correct_answers=correct_answers,
                )
            )
