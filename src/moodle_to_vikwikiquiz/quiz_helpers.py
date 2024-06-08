import re

from bs4 import Tag

# future: report false positive to JetBrains developers
# noinspection PyPackages
from .question import Question

# noinspection PyPackages
from .question_types import QuestionType


def get_question_type(question: Tag) -> QuestionType:
    if question.find("input", type="radio"):
        return QuestionType.SingleChoice
    elif question.find("input", type="checkbox"):
        return QuestionType.MultipleChoice
    else:
        raise NotImplementedError("Question type not implemented.")


def get_grading_of_question(question: Tag) -> tuple[bool, float, float]:
    correctly_answered: bool

    found_tag = question.find("div", class_="grade")
    assert isinstance(found_tag, Tag)

    grading_text = found_tag.text
    numbers = re.findall(r"\d+\.\d+", grading_text)
    grade = float(numbers[0])
    maximum_points = float(numbers[1])
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
) -> None:
    if len(correct_answers) == len(answer_texts) - 1:
        correct_answers.append(
            get_id_of_only_remaining_answer(answer_texts, correct_answers)
        )
        return
    print(f"\n\nQuestion: '{question_text}'")
    match len(correct_answers):
        case 0:
            print("\nI see that none of your answers were correct.")
        case 1:
            print(
                f"\nI see that answer {correct_answers[0]} is correct, "
                f"but there might be additional correct answers because you only got {grade:g} points out of {maximum_points:g}."
            )
        case _:
            print(
                f"\nI see that answers {correct_answers} are correct, "
                f"but this list may be incomplete because you only got {grade:g} points out of {maximum_points:g}."
            )
    print(f"\nThe possible answers are:")
    assert isinstance(answer_texts, list)
    # report false positive to mypy developers
    for j, answer in enumerate(answer_texts):  # type: ignore
        print(f"#{j + 1}\t{answer}")
    print()
    get_missing_correct_answers(answer_texts, correct_answers, question_type)


def get_id_of_only_remaining_answer(
    answer_texts: list[str], correct_answers: list[int]
) -> int:
    for i, answer in enumerate(answer_texts, 1):
        if i not in correct_answers:
            return i


def get_missing_correct_answers(
    answer_texts: list[str], correct_answers: list[int], question_type: QuestionType
) -> None:
    while len(correct_answers) < len(answer_texts):
        additional_correct_answer = input(
            f"Please enter a missing correct answer (if there is any remaining) then press Enter: "
        )
        if additional_correct_answer == "":
            break
        correct_answers.append(int(additional_correct_answer))
        if question_type == QuestionType.SingleChoice:
            break


def get_answers(question: Tag) -> tuple[list[str], list[int]]:
    answers = question.find("div", class_="answer")
    assert isinstance(answers, Tag)
    answer_texts: list[str] = []
    correct_answers: list[int] = []
    i = 1
    for answer in answers:
        try:
            assert isinstance(answer, Tag)
        except AssertionError:
            continue
        found_tag = answer.find("div", class_="ml-1")
        assert isinstance(found_tag, Tag)
        answer_text = found_tag.text.rstrip(".\n")
        answer_text = format_latex_as_wikitext(answer_text)
        answer_texts.append(answer_text)
        if "correct" in answer["class"]:
            correct_answers.append(i)
        i += 1
    return answer_texts, correct_answers


def get_question_text(question: Tag) -> str:
    found_tag = question.find("div", class_="qtext")
    assert isinstance(found_tag, Tag)
    return found_tag.text


def format_latex_as_wikitext(text: str) -> str:
    text = re.sub(r"^\\\(", "<math>", text)
    text = re.sub(r"\\\)$", "</math>", text)
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
                existing_question.correct_answers.append(len(existing_question.answers))
