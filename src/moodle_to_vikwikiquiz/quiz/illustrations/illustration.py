from pathlib import Path
import re

from .state_of_illustrations import StateOfIllustrations  # type: ignore


def remove_wiki_unsafe_characters(upload_filename):
    upload_filename = re.sub(r"[{\[]", "(", upload_filename)
    upload_filename = re.sub(r"[}\]]", ")", upload_filename)
    return upload_filename


class Illustration:
    def __init__(
        self,
        upload_filename: str,
        size_in_pixels: int,
        state_of_illustrations: StateOfIllustrations,
        original_file_path: Path | None = None,
    ) -> None:
        assert isinstance(upload_filename, str)
        upload_filename = remove_wiki_unsafe_characters(upload_filename)
        self.upload_filename = upload_filename

        assert isinstance(size_in_pixels, int)
        self.size_in_pixels = size_in_pixels

        assert isinstance(state_of_illustrations, StateOfIllustrations)
        self.state_of_illustrations = state_of_illustrations

        if original_file_path:
            assert isinstance(original_file_path, Path)
        self.original_file_path = original_file_path

    def __str__(self) -> str:
        if (
            self.state_of_illustrations == StateOfIllustrations.YesAndAvailable
            or self.state_of_illustrations == StateOfIllustrations.YesButUnavailable
        ):
            return f"\n[[Fájl:{self.upload_filename}|keret|keretnélküli|{self.size_in_pixels}px]]"
        else:
            raise ValueError(
                "No images were expected in the quiz but one image filename was requested!"
            )
