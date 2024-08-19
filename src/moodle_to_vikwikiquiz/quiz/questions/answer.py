# noinspection PyPackages
from ..illustrations.illustration import Illustration  # type: ignore

# noinspection PyPackages
from ..quiz_element import QuizElement  # type: ignore

# noinspection PyPackages
from ..illustrations.state_of_illustrations import StateOfIllustrations  # type: ignore


class Answer(QuizElement):
    def __init__(
        self, text: str, correct: bool, illustration: Illustration | None = None
    ) -> None:
        super().__init__(text, illustration)

        assert isinstance(correct, bool)
        self.correct = correct
