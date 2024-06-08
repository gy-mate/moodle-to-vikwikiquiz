from argparse import ArgumentParser
import logging
import os.path
import sys
from urllib.parse import urlencode
import webbrowser

# future: delete the comment below when stubs for the package below are available
import pyperclip  # type: ignore

# future: report false positive to JetBrains developers
# noinspection PyPackages
from .grading_types import GradingType  # type: ignore

# noinspection PyPackages
from .quiz import Quiz  # type: ignore


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="increase output verbosity"
    )
    parser.add_argument(
        "source_directory", help="the directory to import questions from"
    )
    parser.add_argument("parent_article", help="the parent article of the quiz")
    parser.add_argument(
        "-n", "--new", action="store_true", help="create a new article for the quiz"
    )
    parser.add_argument("title", help="the title of the quiz")
    parser.add_argument("-g", "--grading", help="the grading type of the quiz")
    args = parser.parse_args()

    configure_logging(args.verbose)
    logging.getLogger(__name__).debug("Program started...")

    full_source_directory = args.source_directory
    if args.grading == "+":
        grading = GradingType.Kind
    elif args.grading == "-":
        grading = GradingType.Strict
    else:
        grading = None
    quiz = Quiz(parent_article=args.parent_article, title=args.title, grading=grading)
    quiz.import_files(full_source_directory)

    quiz_wikitext = str(quiz)
    if args.new:
        wiki_domain = "https://test.vik.wiki"
        webbrowser.open_new_tab(f"{wiki_domain}/index.php?title=Speciális:Belépés")
        input("Please log in to the wiki then press Enter to continue...")
        parameters = {
            "action": "edit",
            "preload": "Sablon:Előbetöltés",
            "preloadparams[]": quiz_wikitext,
            "summary": "Kvíz létrehozása a https://github.com/gy-mate/moodle-to-vikwikiquiz segítségével importált Moodle-kvízekből",
        }
        webbrowser.open_new_tab(
            f"{wiki_domain}/wiki/{args.title}?{urlencode(parameters)}"
        )
    else:
        pyperclip.copy(quiz_wikitext)
        print("The wikitext of the quiz has been copied to the clipboard!")
    logging.getLogger(__name__).debug("...program finished!")


def configure_logging(verbose: bool) -> None:
    if verbose:
        logging.basicConfig(
            encoding="utf-8",
            handlers=[
                logging.StreamHandler(),
            ],
            format='%(asctime)s [%(levelname)s] "%(pathname)s:%(lineno)d": %(message)s',
            level=logging.DEBUG,
        )
    else:
        logging.basicConfig(
            encoding="utf-8",
            handlers=[
                logging.StreamHandler(sys.stdout),
            ],
            format="[%(levelname)s]: %(message)s",
            level=logging.INFO,
        )


if __name__ == "__main__":
    main()
