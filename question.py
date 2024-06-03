from grading_types import GradingType
from question_types import QuestionType


class Question:
    def __init__(
        self,
        q_type: QuestionType,
        correct_answers: list[int],
        grading: GradingType,
        answers: list[str],
    ):
        self.q_type = q_type
        self.correct_answers = correct_answers
        self.grading = grading
        self.answers = answers

    def __str__(self) -> str:
        text = (
            f"{{{{kvízkérdés"
            f"|típus={self.q_type}"
            f"|válasz={", ".join(str(self.correct_answers))}"
            f"|pontozás={self.grading}}}}}"
        )
        for answer in self.answers:
            text += f"\n# {answer}"
        return text
