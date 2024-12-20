from bs4 import Tag

from ...helpers import prettify  # type: ignore
from .answer import Answer  # type: ignore
from ..question_types import QuestionType  # type: ignore


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


def get_correct_answers_if_provided(question: Tag) -> set[str | None]:
    tag = question.find("div", class_="rightanswer")
    correct_answers: set[str | None] = set()

    if tag:
        assert isinstance(tag, Tag)
        hint_text = prettify(tag.text)
        single_correct_answer_description_translations = [
            "A helyes válasz: ",
            "The correct answer is: ",
        ]
        for (
            correct_answer_description
        ) in single_correct_answer_description_translations:
            if correct_answer_description in hint_text:
                correct_answer = hint_text.removeprefix(correct_answer_description)
                correct_answers.add(correct_answer)
                return correct_answers

        multiple_correct_answer_description_translations = [
            "A helyes válaszok: ",
            "The correct answers are: ",
        ]
        for (
            correct_answer_description
        ) in multiple_correct_answer_description_translations:
            if correct_answer_description in hint_text:
                correct_answer_tags = tag.find_all("p")
                for correct_answer_tag in correct_answer_tags:
                    correct_answer = correct_answer_tag.text
                    prettified_answer = prettify(correct_answer)
                    correct_answers.add(prettified_answer)
                return correct_answers

        if tag.find("img"):
            pass
            return correct_answers

        raise NotImplementedError(
            f"Correct answers could not be extracted from '{hint_text}'!"
        )
    else:
        return correct_answers
