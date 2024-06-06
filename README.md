# moodle-to-vikwikiquiz

![Lines of code](https://img.shields.io/badge/lines_of_code-200+-blue)
[![Build status](https://scrutinizer-ci.com/g/gy-mate/homebrew-moodle-to-vikwikiquiz/badges/build.png?b=main)](https://scrutinizer-ci.com/g/gy-mate/homebrew-moodle-to-vikwikiquiz/build-status/main)
[![Code quality](https://img.shields.io/scrutinizer/quality/g/gy-mate/homebrew-moodle-to-vikwikiquiz/main)](https://scrutinizer-ci.com/g/gy-mate/homebrew-moodle-to-vikwikiquiz/)
[![Type hinting used](https://img.shields.io/badge/type_hinting-used-brightgreen)](https://docs.python.org/3/library/typing.html)
[![Code style: Black](https://img.shields.io/badge/code_style-black-black.svg)](https://github.com/psf/black)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request)


## 📖 About

A program for converting a graded Moodle quiz saved as an HTML file to a [vik.viki quiz](https://vik.wiki/wiki/Segítség:Kvíz) wikitext.


## 📋 Features

* Imports multiple HTML files at once
* Supports single and multiple choice questions
* Creates placeholders for illustrations
* Asks for correct answers if it can't be determined from a graded question
* Deduplicates questions with the same text


## 📥 Installation

1. [Install Homebrew](https://brew.sh/#:~:text=Install%20Homebrew)
2. Run the following command in the terminal:

  ```bash
  brew install gy-mate/moodle-to-vikwikiquiz/moodle-to-vikwikiquiz
  ```


## 🧑‍💻 Usage

```text
moodle-to-vikwikiquiz [--verbose|-v] [[--grading|-g] grading_method] [[--output|-o] destination_file] source_directory parent_article title
```

Parameters:
* `grading_method`: `+` or `-`. See https://vik.wiki/wiki/Segítség:Kvíz#Pontozás for further info.
* `destination_file`: The name of the file where the wikitext quiz should be exported to. Use `.txt` as the extension.
* `source_directory`: The directory where the Moodle quiz HTML files are located. The review page of the quizzes should be downloaded.
* `parent_article`: The article name of the course on [vik.wiki](https://vik.wiki/).
* `title`: How the quiz should be named on [vik.wiki](https://vik.wiki/). This usually is in the following form: `[course name] kvíz – [exam name]`.

Example:
* Convert all [Elektronika alapjai](https://vik.wiki/wiki/Elektronika_alapjai) Moodle quizzes downloaded to `~/Downloads/downloaded_ELA_quizzes`:
```bash
moodle-to-vikwikiquiz --grading - ~/Downloads/downloaded_ELA_quizzes "Elektronika alapjai" "Elektronika alapjai kvíz – vizsga"
```

Always check the output before uploading it to [vik.wiki](https://vik.wiki/). 
Upload all images and add their filenames to the quiz manually on [vik.wiki](https://vik.wiki/).

## 📜 License

This project is licensed under the _GNU General Public License v3.0_.
See the [license](copying.txt) file (or the _GPL-3.0 license_ tab on GitHub) for its full text.