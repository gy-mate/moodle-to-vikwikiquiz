from argparse import Namespace
import logging
from platform import system
from urllib.parse import quote, urlencode
from webbrowser import open_new_tab

from pyperclip import copy  # type: ignore

from .helpers import clear_terminal, remove_uploaded_files, wait_for_pastebot_to_recognize_copy  # type: ignore
from .quiz.illustrations.state_of_illustrations import StateOfIllustrations  # type: ignore
from .quiz.quiz import Quiz  # type: ignore


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
    copy(quiz_wikitext)
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
    open_new_tab(url)
    print(
        "\nThe edit page of the quiz article has been opened in your browser!", end=" "
    )
    if args.new:
        print("Please follow the instructions there.")


def open_article_paste_text(args: Namespace, quiz_wikitext: str, url: str) -> None:
    copy(quiz_wikitext)
    print(
        "\nThe wikitext of the quiz has been copied to the clipboard! "
        "This will be overwritten but you may recall it later if you use an app like Pastebot."
    )
    wait_for_pastebot_to_recognize_copy()
    if args.verbose:
        copy(url)
        print("The URL has been copied to the clipboard!")
    open_new_tab(url)
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
        copy(url)
        print(
            "\nThis URL has been copied to the clipboard! "
            "It will be overwritten but you may recall it later if you use an app like Pastebot."
        )
        wait_for_pastebot_to_recognize_copy()
    parameters_for_opening_edit["summary"] = parameters_for_opening_edit[
        "summary"
    ].replace("bővítése", "létrehozása")


def get_article_instructions(
    quiz: Quiz, wiki_domain: str
) -> tuple[str, dict[str, str], dict[str, str], dict[str, str]]:
    wikitext_instructions = """
<!-- További teendőid (ebben a sorrendben):
• e komment feletti sorba illeszd be a vágólapodra másolt tartalmat
• kattints az 'Előnézet megtekintése' gombra"""
    operating_system = system()
    wiki_modifier_keys = {
        "Darwin": "Control-Option",
        "Linux": "Alt-Shift",
        "Windows": "Alt-Shift",
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
                "Windows": "Ctrl-L",
            }
            print(
                f"""The batch upload page of the wiki will now be opened. After that, please...
• click on 'Fájlok kiválasztása...'"""
            )
            if operating_system == "Darwin" or operating_system == "Linux":
                copy(str(upload_directory))
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
            open_new_tab(
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
    return (
        operating_system,
        parameters_for_opening_edit,
        wiki_editor_keys,
        wiki_modifier_keys,
    )


def log_in_to_wiki(wiki_domain: str) -> None:
    input(
        """Let's log in to the wiki! Please...
• if you see the login page, log in
• when you see the main page of the wiki, return here.

Please press Enter to open the login page..."""
    )
    open_new_tab(f"{wiki_domain}/index.php?title=Speciális:Belépés")
    input("Please press Enter if you've logged in...")
    clear_terminal()
