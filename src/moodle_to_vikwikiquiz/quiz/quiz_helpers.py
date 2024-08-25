import os
from pathlib import Path
import re
from urllib.parse import unquote, urlparse
import uuid

from bs4 import Tag

# noinspection PyPackageRequirements
from plum import dispatch
from pylatexenc.latexencode import unicode_to_latex  # type: ignore

from .illustrations.illustration import Illustration  # type: ignore
from .questions.answer import Answer  # type: ignore
from .quiz_element import QuizElement  # type: ignore
from .illustrations.state_of_illustrations import StateOfIllustrations  # type: ignore
from .questions.question import Question  # type: ignore
from .questions.question_types import QuestionType  # type: ignore


def get_question_type(question: Tag) -> QuestionType:
    if question.find("input", type="radio"):
        return QuestionType.SingleChoice
    elif question.find("input", type="checkbox"):
        return QuestionType.MultipleChoice
    else:
        raise NotImplementedError("Question type not implemented.")


def get_grading_of_question(question: Tag) -> tuple[bool, float | None, float]:
    correctly_answered: bool

    found_tag = question.find("div", class_="grade")
    assert isinstance(found_tag, Tag)

    grading_text = found_tag.text
    numbers_in_capture_groups: list[tuple[str, str]] = re.findall(
        r"(\d+)([.,]\d+)?", grading_text
    )
    numbers = [
        whole + fraction.replace(",", ".")
        for whole, fraction in numbers_in_capture_groups
    ]
    grade: float | None = None
    match len(numbers):
        case 1:
            maximum_points = float(numbers[0])
        case 2:
            grade = float(numbers[0])
            maximum_points = float(numbers[1])
        case _:
            raise NotImplementedError(
                f"{len(numbers)} grade numbers found in '{grading_text}'!"
            )
    if grade == maximum_points:
        correctly_answered = True
    else:
        correctly_answered = False
    return correctly_answered, grade, maximum_points


def get_correct_answers(
    answers: set[Answer],
    grade: float,
    maximum_points: float,
    question_text: str,
    question_type: QuestionType,
    filename: str,
) -> None:
    number_of_current_correct_answers = 0
    list_of_answers = list(answers)
    correct_answers: list[Answer] = []
    for answer in answers:
        if answer.correct:
            number_of_current_correct_answers += 1
            correct_answers.append(answer)

    if number_of_current_correct_answers == len(answers) - 1:
        for answer in answers:
            if not answer.correct:
                answer.correct = True
                return
    print(f"File:\t\t{filename}")
    print(f"Question:\t'{question_text}'")
    match number_of_current_correct_answers:
        case 0:
            print("\nI couldn't determine any correct answers for sure.", end=" ")
        case 1:
            print(
                f"\nI see that answer #{list_of_answers.index(correct_answers[0]) + 1} is correct, "
                f"but there might be additional correct answers because you only got {grade:g} points out of {maximum_points:g}.",
                end=" ",
            )
        case _:
            correct_answer_indexes: list[int] = []
            for correct_answer in correct_answers:
                correct_answer_indexes.append(list_of_answers.index(correct_answer) + 1)
            print(
                f"\nI see that answers {correct_answer_indexes} are correct, "
                f"but this list may be incomplete because you only got {grade:g} points out of {maximum_points:g}.",
                end=" ",
            )
    print(f"The possible answers are:", end="\n\n")
    for j, answer in enumerate(list_of_answers):
        print(f"#{j + 1}\t{answer}")
    print()
    get_missing_correct_answers(correct_answers, list_of_answers, question_type)


def get_missing_correct_answers(
    correct_answers: list[Answer],
    list_of_answers: list[Answer],
    question_type: QuestionType,
) -> None:
    while True:
        get_input_for_missing_correct_answers(
            list_of_answers, correct_answers, question_type
        )
        for answer in list_of_answers:
            if answer.correct:
                return
        print("Error: no correct answers were provided!", end="\n\n")


def get_input_for_missing_correct_answers(
    answers: list[Answer], correct_answers: list[Answer], question_type: QuestionType
) -> None:
    while len(correct_answers) < len(answers):
        additional_correct_answer = input(
            f"Please enter a missing correct answer (if there are any remaining) then press Enter: "
        )
        if additional_correct_answer == "":
            break
        elif not additional_correct_answer.isdigit():
            print("Error: an integer was expected!", end="\n\n")
            continue
        elif int(additional_correct_answer) - 1 not in range(len(answers)):
            print(
                "Error: the number is out of the range of possible answers!", end="\n\n"
            )
            continue
        elif int(additional_correct_answer) in correct_answers:
            print(
                "Error: this answer is already in the list of correct answers!",
                end="\n\n",
            )
            continue
        answers[int(additional_correct_answer) - 1].correct = True
        if question_type == QuestionType.SingleChoice:
            break


def prettify(text: str) -> str:
    text = strip_whitespaces(text)
    text = format_latex_as_wikitext(text)
    return text


def strip_whitespaces(text: str) -> str:
    text = text.strip("., \n")
    text = re.sub(r" \n|\r\n|\s{2}", " ", text)
    return text


def get_correct_answers_if_provided(question: Tag) -> set[str | None]:
    tag = question.find("div", class_="rightanswer")
    correct_answers: set[str | None] = set()
    if tag:
        assert isinstance(tag, Tag)
        hint_text = prettify(tag.text)
        if only_correct_answer := re.findall(
            r"(?<=The correct answer is: ).+", hint_text
        ):
            assert only_correct_answer
            prettified_answer = prettify(only_correct_answer[0])
            correct_answers.add(prettified_answer)
        elif hint_text.find("The correct answers are: ") != -1:
            correct_answer_tags = tag.find_all("p")
            for correct_answer_tag in correct_answer_tags:
                correct_answer = correct_answer_tag.text
                correct_answers.add(prettify(correct_answer))
        elif tag.find("img"):
            pass
        else:
            raise NotImplementedError(
                f"Correct answers could not be extracted from '{hint_text}'!"
            )
    return correct_answers


def answer_is_correct(
    answer: Tag,
    answer_text: str,
    grade: float,
    maximum_points: float,
    correct_answers: set[str | None],
) -> bool:
    if correct_answers and answer_text in correct_answers:
        return True
    elif "correct" in answer["class"]:
        return True
    elif grade == maximum_points:
        answer_input_element = answer.find("input")
        assert isinstance(answer_input_element, Tag)
        if answer_input_element.has_attr("checked"):
            return True
    return False


def get_question_data(
    question: Tag,
    quiz_name: str,
    element: QuizElement,
    state_of_illustrations: StateOfIllustrations,
    current_folder: Path,
) -> tuple[str, Illustration]:
    found_tag = question.find("div", class_="qtext")
    assert isinstance(found_tag, Tag)
    question_text = get_question_text(found_tag)
    illustration = get_element_illustration(
        found_tag,
        question_text,
        quiz_name,
        element,
        state_of_illustrations,
        current_folder,
    )
    return question_text, illustration


def get_question_text(found_tag: Tag) -> str:
    assert isinstance(found_tag, Tag)
    text = re.sub(r"\s?\r?\n\s?", " ", found_tag.text)
    text = text.rstrip()
    text = format_latex_as_wikitext(text)
    return text


def get_element_illustration(
    tag: Tag,
    element_text: str,
    quiz_name: str,
    element: QuizElement,
    state_of_illustrations: StateOfIllustrations,
    current_folder: Path,
    question_name: str | None = None,
) -> Illustration | None:
    if image := tag.find("img"):
        assert isinstance(image, Tag)
        illustration_url = image["src"]
        assert isinstance(illustration_url, str)
        illustration_url_parsed = urlparse(illustration_url)
        illustration_url_parsed = illustration_url_parsed._replace(query="")
        illustration_url_string = illustration_url_parsed.geturl()
        illustration_path_string = unquote(illustration_url_string)
        illustration_path = Path(illustration_path_string)
        original_file_path_string = os.path.join(current_folder, illustration_path)
        original_file_path = Path(original_file_path_string)
        extension = original_file_path.suffix

        if element is Question:
            illustration_size = 500
        elif element is Answer:
            illustration_size = 250
        else:
            raise ValueError(f"Unexpected QuizElement type: {element}!")

        if element_text == "":
            assert question_name
            max_question_name_length = 15
            if len(question_name) > max_question_name_length:
                question_name = f"{question_name[:max_question_name_length]}…"
            upload_filename = create_upload_filename(
                quiz_name,
                question_name,
                extension,
                make_unique=True,
            )
        else:
            upload_filename = create_upload_filename(quiz_name, element_text, extension)
            if filename_too_long(upload_filename):
                upload_filename = truncate_filename(element_text, extension, quiz_name)

        return Illustration(
            upload_filename=upload_filename,
            size_in_pixels=illustration_size,
            state_of_illustrations=state_of_illustrations,
            original_file_path=original_file_path,
        )
    else:
        return None


def truncate_filename(element_text: str, extension: str, quiz_name: str) -> str:
    number_of_element_text_words = 5
    while number_of_element_text_words > 1:
        split_element_text = element_text.split()
        split_truncated_element_text = " ".join(
            split_element_text[:number_of_element_text_words]
        )
        upload_filename = create_upload_filename(
            quiz_name, split_truncated_element_text + "…", extension
        )
        if not filename_too_long(upload_filename):
            return upload_filename
        number_of_element_text_words -= 1

    # noinspection PyUnboundLocalVariable
    split_truncated_element_text = split_truncated_element_text[:15]
    upload_filename = create_upload_filename(
        quiz_name, split_truncated_element_text + "…", extension
    )
    return upload_filename


def filename_too_long(upload_filename):
    return len(upload_filename) > 100


def create_upload_filename(
    quiz_name: str, name_of_illustration: str, extension: str, make_unique: bool = False
) -> str:
    upload_filename = f'"{name_of_illustration}"'
    if make_unique:
        random_hash = uuid.uuid4().hex[:6]
        upload_filename += f" – válaszlehetőség {random_hash}"
    upload_filename += f" ({quiz_name}){extension}"
    return upload_filename


@dispatch
def format_latex_as_wikitext(latex: Tag) -> str:
    wikitext = latex.text
    mathjax = latex.find(class_="MathJax").find("span").text
    wikitext = wikitext.replace(mathjax, "", 1)
    wikitext = wikitext.replace(mathjax, f"<math>{unicode_to_latex(mathjax)}</math>")
    return wikitext


@dispatch  # type: ignore
def format_latex_as_wikitext(latex: str) -> str:
    if re.findall(latex_start_anchored := r"^\s?\\?\\\(\s?(\s?\\(?=\\))?", latex):
        wikitext = re.sub(latex_start_anchored, "<math>", latex)
    else:
        latex_start = latex_start_anchored.replace(r"^\s?", "")
        wikitext = re.sub(latex_start, "<math>", latex)

    if re.findall(latex_end_anchored := r"\s*\\?\\\)\s?$", wikitext):
        wikitext = re.sub(latex_end_anchored, "</math>", wikitext)
    else:
        latex_end = latex_end_anchored.replace(r"\s?$", "")
        wikitext = re.sub(latex_end, "</math>", wikitext)
    return wikitext


def question_already_exists(existing_question: Question, question_text: str) -> bool:
    return existing_question.text == question_text


def add_answers_to_existing_question(
    answers: set[Answer], existing_question: Question
) -> None:
    existing_question.answers.update(answers)


def get_if_has_illustration(
    question: Tag, directory: Path, file: Path
) -> StateOfIllustrations:
    if question.find("img", class_="img-responsive") or question.find(
        "img", role="presentation"
    ):
        return get_if_illustrations_available(directory, file)
    else:
        return StateOfIllustrations.Nil


def get_if_illustrations_available(directory: Path, file: Path) -> StateOfIllustrations:
    asset_folder = os.path.join(directory, f"{file.stem}_files")
    if os.path.exists(asset_folder):
        return StateOfIllustrations.YesAndAvailable
    else:
        return StateOfIllustrations.YesButUnavailable


def clear_terminal():
    os.system("clear||cls")
