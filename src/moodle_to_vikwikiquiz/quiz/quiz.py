from contextlib import suppress

# future: report false positive to JetBrains developers
# noinspection PyUnresolvedReferences
from os import getcwd, makedirs, path, rename, walk

# noinspection PyUnresolvedReferences
from pathlib import Path

from re import compile
from shutil import copy

# noinspection PyUnresolvedReferences
from bs4 import BeautifulSoup, Tag

from .questions.answer import Answer  # type: ignore
from .grading_types import GradingType  # type: ignore
from .illustrations.illustration import Illustration  # type: ignore
from .illustrations.state_of_illustrations import StateOfIllustrations  # type: ignore
from .questions.question_types import QuestionType  # type: ignore
from .quiz_helpers import *  # type: ignore
from .questions.question import Question  # type: ignore
from .quiz_element import QuizElement  # type: ignore


def move_illustration_to_upload_folder(
    quiz_element: QuizElement, upload_directory: Path
) -> None:
    if illustration := quiz_element.illustration:
        if not path.exists(upload_directory):
            makedirs(upload_directory)
        original_file_path = illustration.original_file_path.resolve()
        copy(original_file_path, upload_directory)
        current_file_path = upload_directory / illustration.original_file_path.name
        new_file_path = current_file_path.parent / illustration.upload_filename
        rename(current_file_path, new_file_path)


class Quiz:
    def __init__(
        self,
        title: str,
        parent_article: str | None = None,
        grading: GradingType | None = None,
    ) -> None:
        assert isinstance(title, str)
        self.title = title

        if parent_article:
            assert isinstance(parent_article, str)
        self.parent_article = parent_article

        if grading:
            assert isinstance(grading, GradingType)
        self.grading = grading
        self.new = True if grading else False

        self.questions: set[Question] = set()
        self.state_of_illustrations = StateOfIllustrations.Nil

    def __str__(self) -> str:
        text = ""
        if self.new:
            text += f"""{{{{Vissza | {self.parent_article}}}}}
{{{{moodle-to-vikwikiquiz reklám}}}}

{{{{Kvízoldal
| cím = {self.title}
| pontozás = {self.grading.value}
}}}}\n"""
        for question in self.questions:
            text += f"\n\n\n{question}"
        text += "\n"
        return text

    def import_file_or_files(self, source_path: Path, recursively: bool) -> None:
        if not path.exists(source_path):
            raise FileNotFoundError(f"'{path}' does not exist!")
        elif path.isfile(source_path):
            self.import_questions(source_path, source_path.parent)
        else:
            self.import_files(source_path, recursively)

        if not self.questions:
            raise ValueError(f"No questions were imported from '{path}'!")

    def import_files(self, source_path: Path, recursively: bool) -> None:
        for directory, subdirectories, files in walk(source_path):
            for file in files:
                self.import_questions(Path(file), Path(directory))
            if not recursively:
                break

    def import_questions(self, file: Path, directory: Path) -> None:
        file_path = path.join(directory, file)
        with open(file_path, "rb") as source_file:
            webpage = BeautifulSoup(source_file, "html.parser")

            accepted_questions = webpage.find_all(
                "div", class_=compile(r"multichoice|calculatedmulti|truefalse")
            )
            for question in accepted_questions:
                self.import_question(question, Path(file_path), directory, file)
                clear_terminal()  # type: ignore

    def import_question(
        self,
        question: Tag,
        file_path: Path,
        directory: Path,
        file: Path,
    ) -> None:
        if self.state_of_illustrations == StateOfIllustrations.Nil:
            self.state_of_illustrations = get_if_has_illustration(question, directory, file)  # type: ignore
        with suppress(NotImplementedError):
            question_type = get_question_type(question)  # type: ignore
        correctly_answered, grade, maximum_points = get_grading_of_question(question)  # type: ignore
        # noinspection PyTypeChecker
        question_text, illustration = get_question_data(  # type: ignore
            question,
            self.title,
            Question,
            self.state_of_illustrations,
            Path(directory),
        )
        answers, id_of_correct_answers, all_correct_answers_known = self.get_answers(  # type: ignore
            question, grade, maximum_points, directory, file
        )
        if not correctly_answered and not all_correct_answers_known:
            get_correct_answers(  # type: ignore
                answers,
                grade,
                maximum_points,
                question_text,
                question_type,
                path.basename(file_path),
            )
        self.add_question_if_new(
            question_type,
            question_text,
            self.state_of_illustrations,
            illustration,
            answers,
        )

    def get_answers(
        self,
        question: Tag,
        grade: float,
        maximum_points: float,
        current_folder: Path,
        file: Path,
    ) -> tuple[set[Answer], set[int], bool]:
        answers = question.find("div", class_="answer")
        correct_answers = get_correct_answers_if_provided(question)  # type: ignore
        all_correct_answers_known = bool(correct_answers)
        assert isinstance(answers, Tag)
        answers_to_add: set[Answer] = set()
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
                if self.state_of_illustrations == StateOfIllustrations.Nil:
                    self.state_of_illustrations = get_if_illustrations_available(current_folder, file)  # type: ignore
                question_text_tag = question.find("div", class_="qtext")
                question_text = get_question_text(question_text_tag)  # type: ignore
                # noinspection PyTypeChecker
                illustration = get_element_illustration(  # type: ignore
                    found_tag,
                    answer_text,
                    self.title,
                    Answer,
                    self.state_of_illustrations,
                    current_folder,
                    question_text,
                )
            is_correct = answer_is_correct(  # type: ignore
                answer, answer_text, grade, maximum_points, correct_answers
            )
            answers_to_add.add(Answer(answer_text, is_correct, illustration))
            i += 1
        return answers_to_add, id_of_correct_answers, all_correct_answers_known

    def add_question_if_new(
        self,
        question_type: QuestionType,
        question_text: str,
        has_illustration: StateOfIllustrations,
        illustration: Illustration | None,
        answers: set[Answer],
    ) -> None:
        for existing_question in self.questions:
            if question_already_exists(  # type: ignore
                existing_question,
                Question(
                    q_type=question_type,
                    text=question_text,
                    state_of_illustrations=has_illustration,
                    answers=answers,
                    illustration=illustration,
                ),
            ):
                add_answers_to_existing_question(  # type: ignore
                    answers, existing_question
                )
                break
        else:
            self.add_question(
                answers,
                has_illustration,
                illustration,
                question_text,
                question_type,
            )

    def add_question(
        self,
        answers: set[Answer],
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
                    illustration=illustration,
                )
            )
        except AssertionError:
            print(
                f"Error: question '{question_text}' was not added to the quiz because it wasn't processed correctly!"
            )

    def get_illustrations_ready_for_upload(self) -> Path | None:
        upload_directory = Path(path.join(getcwd(), "to_upload"))
        for question in self.questions:
            move_illustration_to_upload_folder(question, upload_directory)
            for answer in question.answers:
                if answer.illustration:
                    move_illustration_to_upload_folder(answer, upload_directory)
        if path.exists(upload_directory):
            return upload_directory
        else:
            return None
