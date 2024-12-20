from os import system
from pathlib import Path
from time import sleep

from send2trash import send2trash  # type: ignore


def clear_terminal() -> None:
    system("clear||cls")


def wait_for_pastebot_to_recognize_copy() -> None:
    print("Waiting 2 seconds for Pastebot to recognize it...")
    sleep(2)
    print("...done!")


def remove_uploaded_files(folder: Path) -> None:
    send2trash(folder)
