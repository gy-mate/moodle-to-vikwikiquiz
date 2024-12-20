from re import sub

from .illustrations.illustration import Illustration  # type: ignore
from .questions.helpers import format_latex_as_wikitext  # type: ignore
from .quiz_element import QuizElement  # type: ignore
from .illustrations.state_of_illustrations import StateOfIllustrations  # type: ignore
from .questions.question import Question  # type: ignore
from .questions.question_types import QuestionType  # type: ignore


def prettify(text: str) -> str:
    text = strip_whitespaces(text)
    text = format_latex_as_wikitext(text)
    return text


def strip_whitespaces(text: str) -> str:
    text = text.strip("., \n")
    text = sub(r" \n|\r\n|\s{2}", " ", text)
    return text
