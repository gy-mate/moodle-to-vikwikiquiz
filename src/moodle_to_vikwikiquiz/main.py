from argparse import ArgumentParser
import logging
import os.path
import sys

from .grading_types import GradingType
from .quiz import Quiz


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="increase output verbosity"
    )
    parser.add_argument(
        "source_directory", help="the directory to import questions from"
    )
    parser.add_argument("parent_article", help="the parent article of the quiz")
    parser.add_argument("title", help="the title of the quiz")
    parser.add_argument("-g", "--grading", help="the grading type of the quiz")
    parser.add_argument("-o", "--output", help="the output file")
    args = parser.parse_args()

    configure_logging(args.verbose)
    logging.getLogger(__name__).info("Program started...")

    full_source_directory = args.source_directory
    if args.grading == "+":
        grading = GradingType.Kind
    elif args.grading == "-":
        grading = GradingType.Strict
    else:
        grading = None
    quiz = Quiz(parent_article=args.parent_article, title=args.title, grading=grading)
    quiz.import_files(full_source_directory)

    export_file = f"{full_source_directory}/quiz.txt"
    if requested_export_file := args.output:
        if os.path.exists(requested_export_file):
            export_file = os.path.basename(requested_export_file)
    with open(export_file, "w") as file:
        file.write(str(quiz))

    logging.getLogger(__name__).info("...program finished!")


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
