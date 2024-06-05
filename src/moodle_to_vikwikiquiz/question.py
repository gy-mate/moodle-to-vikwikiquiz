from .grading_types import GradingType
from .question_types import QuestionType


class Question:
    def __init__(
        self,
        q_type: QuestionType,
        text: str,
        illustration: bool,
        answers: list[str],
        correct_answers: list[int],
        grading: GradingType | None = None,
    ):
        self.q_type = q_type
        self.text = text
        self.illustration = illustration
        self.grading = grading
        self.answers = answers
        self.correct_answers = correct_answers

    def __str__(self) -> str:
        text = f"== {self.text} =="
        if self.illustration:
            text += "\n[[Fájl:.png|bélyegkép]]"
        text += f"\n\n{{{{kvízkérdés|típus={self.q_type.value}|válasz={",".join([str(answer) for answer in self.correct_answers])}"
        if self.grading:
            text += f"|pontozás={self.grading}"
        text += "}}"
        for answer in self.answers:
            text += f"\n# {answer}"
        return text

    def __hash__(self) -> int:
        return hash(
            frozenset(
                (
                    self.q_type,
                    self.text,
                    self.answers.sort(),
                    self.correct_answers.sort(),
                    self.grading,
                )
            )
        )
