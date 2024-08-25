from argparse import ArgumentParser, Namespace
import logging
from pathlib import Path
from platform import system
import time
from urllib.parse import quote, urlencode
import webbrowser

# future: delete the comment below when stubs for the package below are available
import pyperclip  # type: ignore
from send2trash import send2trash  # type: ignore

from .quiz.illustrations.state_of_illustrations import StateOfIllustrations  # type: ignore
from .quiz.grading_types import GradingType  # type: ignore
from .quiz.quiz import Quiz  # type: ignore
from .quiz.quiz_helpers import clear_terminal  # type: ignore


def main() -> None:
    args = parse_arguments()
    configure_logging(args.verbose)
    logging.getLogger(__name__).debug("Program started...")

    quiz_title = get_desired_name_of_quiz(args.new)
    if args.new:
        parent_article = get_name_of_parent_article()
        grading = get_grading()
    else:
        parent_article = None
        grading = None
    quiz = Quiz(
        title=quiz_title,
        parent_article=parent_article,
        grading=grading,
    )
    absolute_source_path: Path = args.source_path.resolve()
    quiz.import_file_or_files(
        path=absolute_source_path,
        recursively=args.recursive,
    )
    wiki_domain = "https://vik.wiki"

    input(
        """Let's log in to the wiki! Please...
• if you see the login page, log in
• when you see the main page of the wiki, return here.

Please press Enter to open the login page..."""
    )
    quiz_wikitext = str(quiz)
    webbrowser.open_new_tab(f"{wiki_domain}/index.php?title=Speciális:Belépés")
    input("Please press Enter if you've logged in...")
    clear_terminal()

    print("Great!\n")
    wikitext_instructions = """
<!-- További teendőid (ebben a sorrendben):
• e komment feletti sorba illeszd be a vágólapodra másolt tartalmat
• kattints az 'Előnézet megtekintése' gombra"""
    operating_system = system()
    wiki_modifier_keys = {
        "Darwin": "Control-Option",
        "Linux": "Alt-Shift",
    }
    wiki_editor_keys = {"Show preview": "P", "Publish page": "S"}
    if operating_system == "Darwin" or operating_system == "Linux":
        wikitext_instructions += f" ({wiki_modifier_keys[operating_system]}-{wiki_editor_keys["Show preview"]})"
    wikitext_instructions += """
• javítsd a helyesírást és a formázást (ha szükséges), különös tekintettel a képletekre"""
    match quiz.state_of_illustrations:
        case StateOfIllustrations.YesAndAvailable:
            upload_directory = quiz.get_illustrations_ready_for_upload()
            go_to_folder_keyboard_shortcuts = {
                "Darwin": "Command-Shift-G",
                "Linux": "Ctrl-L",
            }
            print(
                f"""The batch upload page of the wiki will now be opened. After that, please...
• click on 'Fájlok kiválasztása...'"""
            )
            if operating_system == "Darwin" or operating_system == "Linux":
                pyperclip.copy(str(upload_directory))
                print(
                    f"""    • press {go_to_folder_keyboard_shortcuts[operating_system]}
        • paste the content of the clipboard
        • press Enter"""
                )
            else:
                print("    • open the following folder: " + str(upload_directory))
            print(
                """    • select all files in the folder
    • click on 'Upload'
• return here."""
            )
            input("\nPlease press Enter then follow these instructions...")
            webbrowser.open_new_tab(
                f"{wiki_domain}/Speciális:TömegesFeltöltés/moodle-to-vikwikiquiz"
            )
            input("Please press Enter if you're done with uploading...")
            if upload_directory:
                remove_uploaded_files(upload_directory)
            clear_terminal()

            print("Great! I've deleted the uploaded files from your disk.\n")
        case StateOfIllustrations.YesButUnavailable:
            wikitext_instructions += """
• töltsd fel kézzel, egyesével a piros linkekkel formázott illusztrációkat
    • másold ki a megfelelő "Fájl:" wikitext után található generált fájlnevet
    • kattints a szerkesztő eszköztárában található 'Képek és médiafájlok' gombra
    • töltsd fel az illusztrációt"""
        case StateOfIllustrations.Nil:
            pass
    wikitext_instructions += """
• töröld ezt a kommentet
• kattints a 'Lap mentése' gombra"""
    if operating_system == "Darwin" or operating_system == "Linux":
        wikitext_instructions += f" ({wiki_modifier_keys[operating_system]}-{wiki_editor_keys["Publish page"]})"
    wikitext_instructions += """
-->"""
    parameters_for_opening_edit = {
        "action": "edit",
        "summary": "Kvíz bővítése "
        "a https://github.com/gy-mate/moodle-to-vikwikiquiz segítségével importált Moodle-kvíz(ek)ből",
        "preload": "Sablon:Előbetöltés",
        "preloadparams[]": wikitext_instructions,
    }
    clear_terminal()

    create_article(
        args,
        parameters_for_opening_edit,
        quiz_title,
        quiz_wikitext,
        wiki_domain,
        wiki_modifier_keys,
        wiki_editor_keys,
        operating_system,
    )
    logging.getLogger(__name__).debug("Program finished!")


def remove_uploaded_files(folder: Path) -> None:
    send2trash(folder)


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


def create_article(
    args: Namespace,
    parameters_for_opening_edit: dict[str, str],
    quiz_title: str,
    quiz_wikitext: str,
    wiki_domain: str,
    wiki_modifier_keys: dict[str, str],
    wiki_editor_keys: dict[str, str],
    operating_system: str,
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
        url = f"{wiki_domain}/{quiz_title}?{urlencode(parameters_for_opening_edit_with_paste)}"
        if len(url) < 2048:
            return open_article_paste_text(args, quiz_wikitext, url)
        else:
            open_article(args, parameters_for_opening_edit, url)
    else:
        del parameters_for_opening_edit["preload"]
        del parameters_for_opening_edit["preloadparams[]"]
    pyperclip.copy(quiz_wikitext)
    print("\nThe wikitext of the quiz has been copied to the clipboard!")
    url = f"{wiki_domain}/{quote(quiz_title)}?{urlencode(parameters_for_opening_edit)}"
    if not args.new:
        print(
            f"""
The existing article will now be opened for editing. After that, please...
• scroll to the bottom of the wikitext in the editor
• add a new line
• paste the content of the clipboard in that line
• click on the 'Előnézet megtekintése' button ({wiki_modifier_keys[operating_system]}-{wiki_editor_keys["Show preview"]})
• correct the spelling and formatting (if necessary), especially the formulas
• click on the 'Lap mentése' button ({wiki_modifier_keys[operating_system]}-{wiki_editor_keys["Publish page"]})"""
        )
        input("\nPlease press Enter then follow these instructions...")
    webbrowser.open_new_tab(url)
    print(
        "\nThe edit page of the quiz article has been opened in your browser!", end=" "
    )
    if args.new:
        print("Please follow the instructions there.")


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


def open_article(
    args: Namespace, parameters_for_opening_edit: dict[str, str], url: str
) -> None:
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
