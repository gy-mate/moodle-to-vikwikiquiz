from argparse import ArgumentParser, Namespace
import logging
from pathlib import Path
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

    quiz_title = get_desired_name_of_quiz(args.new)
    quiz = Quiz(
        parent_article=get_name_of_parent_article(),
        title=quiz_title,
        grading=get_grading(),
    )
    absolute_source_path: Path = args.source_path.resolve()
    quiz.import_files(
        path=absolute_source_path,
        recursively=args.recursive,
    )

    quiz_wikitext = str(quiz)
    wiki_domain = "https://test.vik.wiki"
    webbrowser.open_new_tab(f"{wiki_domain}/index.php?title=Speciális:Belépés")
    input("Please log in to the wiki then press Enter to continue...")
    parameters_for_opening_edit = {
        "action": "edit",
        "summary": "Kvíz bővítése "
        "a https://github.com/gy-mate/moodle-to-vikwikiquiz segítségével importált Moodle-kvíz(ek)ből",
        "preload": "Sablon:Előbetöltés",
        "preloadparams[]": "<!-- Töröld ki ezt és a következő sort, majd illeszd be a vágólapodra másolt tartalmat! -->",
    }
    clear_terminal()
    create_article(
        args, parameters_for_opening_edit, quiz_title, quiz_wikitext, wiki_domain
    )
    logging.getLogger(__name__).debug("Program finished!")


def parse_arguments() -> Namespace:
    parser = ArgumentParser()
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


def get_name_of_parent_article() -> str:
    while True:
        try:
            input_name = input(
                f"\nPlease enter the name of the vik.wiki article on the corresponding course on then press Enter:\n"
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
                "\nSee https://vik.wiki/wiki/Segítség:Kvíz#Pontozás for further info.\n"
            )
            return GradingType(grading_symbol)
        except ValueError:
            print("This is not a valid grading type!")
        finally:
            clear_terminal()


def create_article(
    args: Namespace,
    parameters_for_opening_edit: dict,
    quiz_title: str,
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
        url = f"{wiki_domain}/wiki/{quiz_title}?{urlencode(parameters_for_opening_edit_with_paste)}"
        if len(url) < 2048:
            return open_article_paste_text(args, quiz_wikitext, url)
        else:
            open_article(args, parameters_for_opening_edit, url)
    pyperclip.copy(quiz_wikitext)
    print("\nThe wikitext of the quiz has been copied to the clipboard!")
    url = f"{wiki_domain}/wiki/{quiz_title}?{urlencode(parameters_for_opening_edit)}"
    webbrowser.open_new_tab(url)
    print(
        "\nThe edit page of the quiz article has been opened in your browser! "
        "Please paste the wikitext and upload illustrations (if any) there manually."
    )


def open_article_paste_text(args: Namespace, quiz_wikitext: str, url: str) -> None:
    pyperclip.copy(quiz_wikitext)
    print(
        "\nThe wikitext of the quiz has been copied to the clipboard! "
        "This will be overwritten but you may recall it later if you use an app like Pastebot."
    )
    wait_for_pastebot_to_recognize_copy()
    if args.verbose:
        pyperclip.copy(url)
        print("The URL has been copied to the clipboard!")
    webbrowser.open_new_tab(url)
    print(
        "\nThe edit page of the new quiz article has been opened in your browser with the wikitext pre-filled! "
        "Please upload illustrations manually, if there are any."
    )
    return


def open_article(args: Namespace, parameters_for_opening_edit: dict, url: str) -> None:
    logging.getLogger(__name__).warning(
        "I can't create the article automatically "
        "because the URL would be too long for some browsers (or the server)."
    )
    if args.verbose:
        pyperclip.copy(url)
        print(
            "\nThis URL has been copied to the clipboard! "
            "It will be overwritten but you may recall it later if you use an app like Pastebot."
        )
        wait_for_pastebot_to_recognize_copy()
    parameters_for_opening_edit["summary"] = parameters_for_opening_edit[
        "summary"
    ].replace("bővítése", "létrehozása")


def wait_for_pastebot_to_recognize_copy() -> None:
    print("Waiting 2 seconds for Pastebot to recognize it...")
    time.sleep(2)
    print("...done!")


if __name__ == "__main__":
    main()
