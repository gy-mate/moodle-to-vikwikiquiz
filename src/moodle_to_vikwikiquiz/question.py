# future: report false positive to JetBrains developers
# noinspection PyPackages
# future: report false positive to mypy developers
from pydantic import BaseModel

# noinspection PyPackages
from .grading_types import GradingType  # type: ignore

# noinspection PyPackages
# future: report false positive to mypy developers
from .question_types import QuestionType  # type: ignore


class Question(BaseModel):
    q_type: QuestionType
    text: str
    illustration: bool
    answers: list[str]
    correct_answers: set[int]
    grading: GradingType | None = None

    def __str__(self) -> str:
        text = f"== {self.text} =="
        if self.illustration:
            text += "\n[[Fájl:.png|keret|keretnélküli|500x500px]]"
        ordered_correct_answers = list(self.correct_answers)
        ordered_correct_answers.sort()
        text += (
            f"\n{{{{kvízkérdés|típus={self.q_type.value}"
            f"|válasz={",".join([str(answer) for answer in ordered_correct_answers])}"
        )
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
                    frozenset(self.correct_answers),
                    self.grading,
                )
            )
        )
