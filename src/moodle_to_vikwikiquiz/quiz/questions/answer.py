from ..illustrations.illustration import Illustration  # type: ignore
from ..quiz_element import QuizElement  # type: ignore
from ..illustrations.state_of_illustrations import StateOfIllustrations  # type: ignore


class Answer(QuizElement):
    def __init__(
        self, text: str, correct: bool, illustration: Illustration | None = None
    ) -> None:
        super().__init__(text, illustration)

        assert isinstance(correct, bool)
        self.correct = correct

    def __hash__(self) -> int:
        object_hash = hash(frozenset((self.text, self.correct, self.illustration)))
        return object_hash

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Answer):
            return False
        return (
            self.text == other.text
            and self.correct == other.correct
            and self.illustration == other.illustration
        )
