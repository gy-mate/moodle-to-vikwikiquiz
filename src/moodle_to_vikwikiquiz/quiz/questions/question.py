from typing_extensions import override

# noinspection PyPackages
from .answer import Answer  # type: ignore

# noinspection PyPackages
from ..grading_types import GradingType  # type: ignore

# noinspection PyPackages
from ..illustrations.illustration import Illustration  # type: ignore

# noinspection PyPackages
from ..quiz_element import QuizElement  # type: ignore

# noinspection PyPackages
from ..illustrations.state_of_illustrations import StateOfIllustrations  # type: ignore

# noinspection PyPackages
# future: report false positive to mypy developers
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
        ordered_correct_answers = [answer for answer in self.answers if answer.correct]
        ordered_correct_answers.sort()
        text += (
            f"\n{{{{kvízkérdés|típus={self.q_type.value}"
            f"|válasz={",".join([str(answer) for answer in ordered_correct_answers])}"
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
                )
            )
        )
