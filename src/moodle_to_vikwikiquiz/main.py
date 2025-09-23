from argparse import ArgumentParser, Namespace
import logging
from pathlib import Path
from sys import version_info

from .wiki import create_article, get_article_instructions, log_in_to_wiki  # type: ignore
from .quiz.illustrations.state_of_illustrations import StateOfIllustrations  # type: ignore
from .quiz.grading_types import GradingType  # type: ignore
from .quiz.quiz import Quiz  # type: ignore
from .helpers import clear_terminal, wait_for_pastebot_to_recognize_copy  # type: ignore


def main() -> None:
    # future: remove the conditional below when https://github.com/linkedin/shiv/issues/268 is fixed
    warn_if_python_version_not_met()

    args = parse_arguments()
    configure_logging(args.verbose)
    logging.getLogger(__name__).debug("Program started...")

    grading, parent_article, quiz_title = ask_user_for_data(args.new)
    quiz = Quiz(
        title=quiz_title,
        parent_article=parent_article,
        grading=grading,
    )

    absolute_source_path: Path = args.source_path.resolve()
    quiz.import_file_or_files(
        source_path=absolute_source_path,
        recursively=args.recursive,
    )

    wiki_domain = "https://vik.wiki"
    log_in_to_wiki(wiki_domain)
    print("Great!\n")

    (
        operating_system,
        parameters_for_opening_edit,
        wiki_editor_keys,
        wiki_modifier_keys,
    ) = get_article_instructions(quiz, wiki_domain)
    create_article(
        args,
        parameters_for_opening_edit,
        quiz_title,
        str(quiz),
        wiki_domain,
        wiki_modifier_keys,
        wiki_editor_keys,
        operating_system,
    )
    logging.getLogger(__name__).debug("Program finished!")


def warn_if_python_version_not_met() -> None:
    if version_info < (3, 12):
        raise SystemError(
            "This app requires Python 3.12 or later. Please upgrade it from https://www.python.org/downloads/!"
        )


def parse_arguments() -> Namespace:
    parser = ArgumentParser(
        "Convert graded and downloaded Moodle quizzes to a vik.viki quiz wikitext."
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="increase output verbosity"
    )
    parser.add_argument(
        "-n",
        "--new",
        action="store_true",
        help="create a new quiz on vik.wiki by automatically opening an edit page for the new article",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="import HTML files from the current directory recursively",
    )
    parser.add_argument(
        "source_path",
        type=Path,
        help="The absolute or relative path of the file or directory where the Moodle quiz HTML files are located. "
        "These HTML files should contain the 'Review' page of the quizzes.",
    )
    return parser.parse_args()


def configure_logging(verbose: bool) -> None:
    if verbose:
        logging.basicConfig(
            encoding="utf-8",
            format='%(asctime)s [%(levelname)s] "%(pathname)s:%(lineno)d": %(message)s',
            level=logging.DEBUG,
        )
    else:
        logging.basicConfig(
            encoding="utf-8",
            format="[%(levelname)s]: %(message)s",
            level=logging.INFO,
        )


def ask_user_for_data(new: bool) -> tuple[GradingType | None, str | None, str]:
    quiz_title = get_desired_name_of_quiz(new)
    if new:
        parent_article = get_name_of_parent_article()
        grading = get_grading()
    else:
        parent_article = None
        grading = None
    return grading, parent_article, quiz_title


def get_name_of_parent_article() -> str:
    while True:
        try:
            input_name = input(
                f"\nPlease enter the name of the vik.wiki article of the corresponding course then press Enter:\n"
            )
            if not input_name:
                raise ValueError("Nothing was entered!")
            return input_name
        except ValueError as error:
            print(error)


def get_desired_name_of_quiz(new: bool) -> str:
    while True:
        try:
            print(
                "\nPlease enter how the quiz should be named on vik.wiki then press Enter!"
                "\nThis is usually in the following form: `[course name] kvíz – [exam name]`. (The ` – [exam name]` can be omitted.)"
            )
            if not new:
                print("This might be an existing article name.")
            input_name = input()
            if not input_name:
                raise ValueError("Nothing was entered!")
            return input_name
        except ValueError as error:
            print(error)


def get_grading() -> GradingType:
    while True:
        try:
            grading_symbol = input(
                "\nPlease enter `+` or `-` as the grading type of the quiz then press Enter!"
                "\nSee https://vik.wiki/Segítség:Kvíz#Pontozás for further info.\n"
            )
            return GradingType(grading_symbol)
        except ValueError:
            print("This is not a valid grading type!")
        finally:
            clear_terminal()


if __name__ == "__main__":
    main()
