import os
import re

from bs4 import Tag

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
    numbers = re.findall(r"\d+\.\d+", grading_text)
    grade: float | None = None
    match len(numbers):
        case 1:
            maximum_points = float(numbers[0])
        case 2:
            grade = float(numbers[0])
            maximum_points = float(numbers[1])
        case _:
            raise NotImplementedError
    if grade == maximum_points:
        correctly_answered = True
    else:
        correctly_answered = False
    return correctly_answered, grade, maximum_points


def complete_correct_answers(
    answer_texts: list[str],
    correct_answers: list[int],
    grade: float,
    maximum_points: float,
    question_text: str,
    question_type: QuestionType,
    file_name: str,
) -> None:
    if len(correct_answers) == len(answer_texts) - 1:
        correct_answers.append(
            get_id_of_only_remaining_answer(answer_texts, correct_answers)
        )
        return
    print(f"File: {file_name}")
    print(f"Question: '{question_text}'")
    match len(correct_answers):
        case 0:
            print("\nI couldn't determine any correct answers for sure.", end=" ")
        case 1:
            print(
                f"\nI see that answer #{correct_answers[0]} is correct, "
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
    answer_texts: list[str], correct_answers: list[int]
) -> int:
    for i, answer in enumerate(answer_texts, 1):
        if i not in correct_answers:
            return i
    raise NotImplementedError


def get_missing_correct_answers(
    answer_texts: list[str], correct_answers: list[int], question_type: QuestionType
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
        correct_answers.append(int(additional_correct_answer))
        if question_type == QuestionType.SingleChoice:
            break


def get_answers(
    question: Tag, grade: float, maximum_points: float
) -> tuple[list[str], list[int]]:
    answers = question.find("div", class_="answer")
    assert isinstance(answers, Tag)
    answer_texts: list[str] = []
    correct_answers: list[int] = []
    i = 1
    for answer in answers:
        if not isinstance(answer, Tag):
            continue
        found_tag = answer.find("div", class_="ml-1")
        assert isinstance(found_tag, Tag)
        answer_text = found_tag.text.rstrip(".\n")
        answer_text = format_latex_as_wikitext(answer_text)
        answer_texts.append(answer_text)
        if answer_is_correct(answer, grade, maximum_points):
            correct_answers.append(i)
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
    text = re.sub(r"\n", " ", found_tag.text)
    return text.rstrip()


def format_latex_as_wikitext(text: str) -> str:
    text = re.sub(r"^(\\)?\\\(( )?(( )?\\(?=\\))?", "<math>", text)
    text = re.sub(r"( \\)?\\\)( )?$", "</math>", text)
    return text


def question_already_exists(existing_question: Question, question_text: str) -> bool:
    return existing_question.text == question_text


def add_answers_to_existing_question(
    answer_texts: list[str], correct_answers: list[int], existing_question: Question
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
