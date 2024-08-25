from typing_extensions import override

from .answer import Answer  # type: ignore
from ..grading_types import GradingType  # type: ignore
from ..illustrations.illustration import Illustration  # type: ignore
from ..quiz_element import QuizElement  # type: ignore
from ..illustrations.state_of_illustrations import StateOfIllustrations  # type: ignore
from .question_types import QuestionType  # type: ignore


class Question(QuizElement):
    def __init__(
        self,
        q_type: QuestionType,
        text: str,
        state_of_illustrations: StateOfIllustrations,
        answers: set[Answer],
        grading: GradingType | None = None,
        illustration: Illustration | None = None,
    ) -> None:
        super().__init__(text, illustration)

        assert isinstance(q_type, QuestionType)
        self.q_type = q_type

        assert isinstance(state_of_illustrations, StateOfIllustrations)
        self.state_of_illustrations = state_of_illustrations

        assert isinstance(answers, set)
        assert answers
        self.answers = answers

        if grading:
            assert isinstance(grading, GradingType)
        self.grading = grading

        if illustration:
            assert isinstance(illustration, Illustration)
        self.illustration = illustration

    @override
    def __str__(self) -> str:
        text = f"== {self.text} =="
        if self.illustration:
            text += str(self.illustration)
        correct_answer_indexes: list[str] = []
        for i, answer in enumerate(self.answers):
            if answer.correct:
                correct_answer_indexes.append(str(i + 1))
        text += (
            f"\n{{{{kvízkérdés|típus={self.q_type.value}"
            f"|válasz={",".join(correct_answer_indexes)}"
        )
        if self.grading:
            text += f"|pontozás={self.grading}"
        text += "}}"
        for answer in self.answers:
            text += f"\n# {str(answer).replace("\n", " ")}"
        return text

    def __hash__(self) -> int:
        return hash(
            frozenset(
                (
                    self.q_type,
                    self.text,
                    frozenset(self.answers),
                    self.grading,
                    self.illustration,
                )
            )
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Question):
            return False
        return (
            self.q_type == other.q_type
            and self.text == other.text
            and self.answers == other.answers
            and self.grading == other.grading
            and self.illustration == other.illustration
        )
