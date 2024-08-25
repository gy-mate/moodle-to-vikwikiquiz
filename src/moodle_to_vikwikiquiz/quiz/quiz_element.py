from .illustrations.illustration import Illustration  # type: ignore


class QuizElement:
    def __init__(
        self,
        text: str,
        illustration: Illustration | None = None,
    ) -> None:
        assert isinstance(text, str)
        self.text = text

        if illustration:
            assert isinstance(illustration, Illustration)
        self.illustration = illustration

    def __str__(self) -> str:
        text = self.text
        if self.illustration:
            text += str(self.illustration)
        return text
