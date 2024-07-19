import os
import re

from bs4 import Tag

# noinspection PyPackageRequirements
from plum import dispatch
from pylatexenc.latexencode import unicode_to_latex  # type: ignore

# future: report false positive to JetBrains developers
# noinspection PyPackages
from .question import Question  # type: ignore

# noinspection PyPackages
from .question_types import QuestionType  # type: ignore


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
        r"(\d+)(\.\d+)?", grading_text
    )
    numbers = [whole + fraction for whole, fraction in numbers_in_capture_groups]
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


def complete_correct_answers(
    answer_texts: list[str],
    correct_answers: set[int],
    grade: float,
    maximum_points: float,
    question_text: str,
    question_type: QuestionType,
    filename: str,
) -> None:
    if len(correct_answers) == len(answer_texts) - 1:
        correct_answers.add(
            get_id_of_only_remaining_answer(answer_texts, correct_answers)
        )
        return
    print(f"File:\t\t{filename}")
    print(f"Question:\t'{question_text}'")
    match len(correct_answers):
        case 0:
            print("\nI couldn't determine any correct answers for sure.", end=" ")
        case 1:
            print(
                f"\nI see that answer #{list(correct_answers)[0]} is correct, "
                f"but there might be additional correct answers because you only got {grade:g} points out of {maximum_points:g}.",
                end=" ",
            )
        case _:
            print(
                f"\nI see that answers {correct_answers} are correct, "
                f"but this list may be incomplete because you only got {grade:g} points out of {maximum_points:g}.",
                end=" ",
            )
    print(f"The possible answers are:", end="\n\n")
    assert isinstance(answer_texts, list)
    # report false positive to mypy developers
    for j, answer in enumerate(answer_texts):  # type: ignore
        print(f"#{j + 1}\t{answer}")
    print()
    while True:
        get_missing_correct_answers(answer_texts, correct_answers, question_type)
        if correct_answers:
            break
        print("Error: no correct answers were provided!", end="\n\n")


def get_id_of_only_remaining_answer(
    answer_texts: list[str], correct_answers: set[int]
) -> int:
    for i, answer in enumerate(answer_texts, 1):
        if i not in correct_answers:
            return i
    raise NotImplementedError


def get_missing_correct_answers(
    answer_texts: list[str], correct_answers: set[int], question_type: QuestionType
) -> None:
    while len(correct_answers) < len(answer_texts):
        additional_correct_answer = input(
            f"Please enter a missing correct answer (if there is any remaining) then press Enter: "
        )
        if additional_correct_answer == "":
            break
        elif not additional_correct_answer.isdigit():
            print("Error: an integer was expected!", end="\n\n")
            continue
        elif int(additional_correct_answer) - 1 not in range(len(answer_texts)):
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
        correct_answers.add(int(additional_correct_answer))
        if question_type == QuestionType.SingleChoice:
            break


def get_answers(
    question: Tag, grade: float, maximum_points: float
) -> tuple[list[str], set[int]]:
    answers = question.find("div", class_="answer")
    assert isinstance(answers, Tag)
    answer_texts: list[str] = []
    correct_answers: set[int] = set()
    i = 1
    for answer in answers:
        if not isinstance(answer, Tag):
            continue
        found_tag = answer.find(class_="ml-1")
        assert isinstance(found_tag, Tag)
        if found_tag.find("img"):
            answer_texts.append("[[Fájl:.png|keret|keretnélküli|250x250px]]")
        elif found_tag.find(class_="MathJax"):
            answer_text = format_latex_as_wikitext(found_tag)
            answer_texts.append(answer_text)
        else:
            match answer_text := found_tag.text:
                case "True":
                    answer_text = "Igaz"
                case "False":
                    answer_text = "Hamis"
                case _:
                    answer_text = answer_text.strip(".\n")
                    answer_text = re.sub(r"\r\n|\s{2}", " ", answer_text)
                    answer_text = format_latex_as_wikitext(answer_text)
            answer_texts.append(answer_text)
        if answer_is_correct(answer, grade, maximum_points):
            correct_answers.add(i)
        i += 1
    return answer_texts, correct_answers


def answer_is_correct(answer: Tag, grade: float, maximum_points: float) -> bool:
    if "correct" in answer["class"]:
        return True
    elif grade == maximum_points:
        answer_input_element = answer.find("input")
        assert isinstance(answer_input_element, Tag)
        if answer_input_element.has_attr("checked"):
            return True
    return False


def get_question_text(question: Tag) -> str:
    found_tag = question.find("div", class_="qtext")
    assert isinstance(found_tag, Tag)
    text = re.sub(r"\s?\r?\n\s?", " ", found_tag.text)
    text = text.rstrip()
    text = format_latex_as_wikitext(text)
    return text


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
    answer_texts: list[str], correct_answers: set[int], existing_question: Question
) -> None:
    # report false positive to mypy developers
    for k, answer in enumerate(answer_texts):  # type: ignore
        if answer not in existing_question.answers:
            assert isinstance(answer, str)
            existing_question.answers.append(answer)
            if k + 1 in correct_answers:
                existing_question.correct_answers.add(len(existing_question.answers))


def get_if_has_illustration(question: Tag) -> bool:
    if question.find("img", class_="img-responsive"):
        return True
    elif question.find("img", role="presentation"):
        return True
    else:
        return False


def clear_terminal():
    os.system("clear||cls")
