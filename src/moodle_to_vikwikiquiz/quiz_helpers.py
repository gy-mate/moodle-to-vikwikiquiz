import re

from bs4 import Tag

from .question import Question


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
) -> None:
    print(
        f"""

Question: '{question_text}'

I see that answers {correct_answers} are correct, but this list may be incomplete because you only got {grade:g} points out of {maximum_points:g}.

The answers are:"""
    )
    assert isinstance(answer_texts, list)
    # report false positive to mypy developers
    for j, answer in enumerate(answer_texts):  # type: ignore
        print(f"#{j + 1}\t{answer}")
    print()
    get_missing_correct_answers(answer_texts, correct_answers)


def get_missing_correct_answers(
    answer_texts: list[str], correct_answers: list[int]
) -> None:
    while True:
        additional_correct_answer = input(
            f"Please enter a missing correct answer (if there is any remaining) then press Enter: "
        )
        if (
            additional_correct_answer == ""
            or len(correct_answers) == len(answer_texts) - 1
        ):
            break
        correct_answers.append(int(additional_correct_answer))


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
        answer_texts.append(found_tag.text.rstrip("."))
        if "correct" in answer["class"]:
            correct_answers.append(i)
        i += 1
    return answer_texts, correct_answers


def get_question_text(question: Tag) -> str:
    found_tag = question.find("div", class_="qtext")
    assert isinstance(found_tag, Tag)
    question_text = found_tag.text
    return question_text


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
