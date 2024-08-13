import contextlib

# future: report false positive to JetBrains developers
# noinspection PyUnresolvedReferences
import os
from pathlib import Path

# future: report false positive to JetBrains developers
# noinspection PyUnresolvedReferences
import re

# future: report false positive to JetBrains developers
# noinspection PyUnresolvedReferences
from bs4 import BeautifulSoup, Tag

# future: report false positive to JetBrains developers
# noinspection PyPackages
# future: report false positive to mypy developers
from .grading_types import GradingType  # type: ignore

# future: report false positive to JetBrains developers
# noinspection PyPackages
from .illustrations import StateOfIllustrations  # type: ignore

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
            raise ValueError(
                "No questions were imported from the provided source path!"
            )

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
        with contextlib.suppress(NotImplementedError):
            question_type = get_question_type(question)  # type: ignore
        correctly_answered, grade, maximum_points = get_grading_of_question(question)  # type: ignore
        question_text = get_question_text(question)  # type: ignore
        answer_texts, id_of_correct_answers, all_correct_answers_known = get_answers(  # type: ignore
            question, grade, maximum_points
        )
        if not correctly_answered and not all_correct_answers_known:
            complete_correct_answers(  # type: ignore
                answer_texts,
                id_of_correct_answers,
                grade,
                maximum_points,
                question_text,
                question_type,
                os.path.basename(file_path),
            )
        has_illustration = get_if_has_illustration(question, subdir, file)  # type: ignore
        self.add_question_no_duplicates(
            question_type,
            question_text,
            has_illustration,
            answer_texts,
            id_of_correct_answers,
        )

    def add_question_no_duplicates(
        self,
        question_type: QuestionType,
        question_text: str,
        has_illustration: StateOfIllustrations,
        answer_texts: list[str],
        correct_answers: set[int],
    ) -> None:
        for existing_question in self.questions:
            if question_already_exists(existing_question, question_text):  # type: ignore
                add_answers_to_existing_question(  # type: ignore
                    answer_texts, correct_answers, existing_question
                )
                break
        else:
            self.add_question(
                answer_texts,
                correct_answers,
                has_illustration,
                question_text,
                question_type,
            )

    def add_question(
        self,
        answer_texts: list[str],
        correct_answers: set[int],
        has_illustration: StateOfIllustrations,
        question_text: str,
        question_type: QuestionType,
    ) -> None:
        try:
            self.questions.add(
                Question(
                    q_type=question_type,
                    text=question_text,
                    illustration=has_illustration,
                    answers=answer_texts,
                    correct_answers=correct_answers,
                )
            )
        except AssertionError:
            print(
                f"Error: question '{question_text}' was not added to the quiz because it wasn't processed correctly!"
            )
