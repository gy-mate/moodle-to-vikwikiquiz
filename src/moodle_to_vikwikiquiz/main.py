from argparse import ArgumentParser, Namespace
import logging
import time
from urllib.parse import urlencode
import webbrowser

# future: delete the comment below when stubs for the package below are available
import pyperclip  # type: ignore

# future: report false positive to JetBrains developers
# noinspection PyPackages
from .grading_types import GradingType  # type: ignore

# noinspection PyPackages
from .quiz import Quiz  # type: ignore

# noinspection PyPackages
from .quiz_helpers import clear_terminal  # type: ignore


def main() -> None:
    args = parse_arguments()
    configure_logging(args.verbose)
    logging.getLogger(__name__).debug("Program started...")

    full_source_directory, grading = get_arguments(args)
    quiz = Quiz(parent_article=args.parent_article, title=args.title, grading=grading)
    quiz.import_files(full_source_directory)

    quiz_wikitext = str(quiz)
    wiki_domain = "https://test.vik.wiki"
    webbrowser.open_new_tab(f"{wiki_domain}/index.php?title=Speciális:Belépés")
    input("Please log in to the wiki then press Enter to continue...")
    parameters_for_opening_edit = {
        "action": "edit",
        "summary": "Kvíz bővítése "
        "a https://github.com/gy-mate/moodle-to-vikwikiquiz segítségével importált Moodle-kvízekből",
    }
    clear_terminal()
    create_article(args, parameters_for_opening_edit, quiz_wikitext, wiki_domain)
    logging.getLogger(__name__).debug("Program finished!")


def create_article(
    args: Namespace,
    parameters_for_opening_edit: dict,
    quiz_wikitext: str,
    wiki_domain: str,
) -> None:
    if args.new:
        parameters_for_opening_edit_with_paste = parameters_for_opening_edit.copy()
        parameters_for_opening_edit_with_paste.update(
            {
                "preload": "Sablon:Előbetöltés",
                "preloadparams[]": quiz_wikitext,
            }
        )
        parameters_for_opening_edit_with_paste["summary"] = (
            parameters_for_opening_edit_with_paste["summary"].replace(
                "bővítése", "létrehozása"
            )
        )
        url = f"{wiki_domain}/wiki/{args.title}?{urlencode(parameters_for_opening_edit_with_paste)}"
        if len(url) >= 2048:
            logging.getLogger(__name__).warning(
                "I can't create the article automatically "
                "because the URL would be too long for some browsers (or the server)."
            )
            if args.verbose:
                pyperclip.copy(url)
                print(
                    "This URL has been copied to the clipboard! "
                    "It will be overwritten but you may recall it later if you use an app like Pastebot."
                )
                wait_for_pastebot_to_recognize_copy()
            parameters_for_opening_edit["summary"] = parameters_for_opening_edit[
                "summary"
            ].replace("bővítése", "létrehozása")
        else:
            pyperclip.copy(quiz_wikitext)
            print(
                "The wikitext of the quiz has been copied to the clipboard! "
                "This will be overwritten but you may recall it later if you use an app like Pastebot."
            )
            wait_for_pastebot_to_recognize_copy()
            if args.verbose:
                pyperclip.copy(url)
                print("The URL has been copied to the clipboard!")
            webbrowser.open_new_tab(url)
            print(
                "The edit page of the new quiz article has been opened in your browser with the wikitext pre-filled!"
            )
            return
    pyperclip.copy(quiz_wikitext)
    print("The wikitext of the quiz has been copied to the clipboard!")
    url = f"{wiki_domain}/wiki/{args.title}?{urlencode(parameters_for_opening_edit)}"
    webbrowser.open_new_tab(url)
    print(
        "The edit page of the quiz article has been opened in your browser! Please paste the wikitext there manually."
    )


def get_arguments(args: Namespace) -> tuple[str, GradingType]:
    full_source_directory = args.source_directory
    match args.grading:
        case "+":
            grading = GradingType.Kind
        case "-":
            grading = GradingType.Strict
        case _:
            grading = None
    return full_source_directory, grading


def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="increase output verbosity"
    )
    parser.add_argument(
        "source_directory",
        help="The absolute path of the directory where the Moodle quiz HTML files are located. "
        "These HTML files should contain the 'Review' page of the quizzes.",
    )
    parser.add_argument(
        "parent_article", help="The article name of the course on vik.wiki."
    )
    parser.add_argument(
        "-n",
        "--new",
        action="store_true",
        help="Create a new quiz on vik.wiki by automatically opening an edit page for the new article.",
    )
    parser.add_argument(
        "title",
        help="How the quiz should be named on [vik.wiki](https://vik.wiki/). "
        "This usually is in the following form: `[course name] kvíz – [exam name]`. "
        "(The hyphen and the part after it can be omitted.) "
        "This might be an existing article name if the `--new` argument is not provided.",
    )
    parser.add_argument(
        "-g",
        "--grading",
        help="`+` or `-`. See https://vik.wiki/wiki/Segítség:Kvíz#Pontozás for further info.",
    )
    return parser.parse_args()


def wait_for_pastebot_to_recognize_copy() -> None:
    print("Waiting 2 seconds for Pastebot to recognize it...")
    time.sleep(2)
    print("...done!")


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


if __name__ == "__main__":
    main()
