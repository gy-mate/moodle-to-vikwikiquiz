# moodle-to-vikwikiquiz

![Lines of code](https://img.shields.io/badge/lines_of_code-400+-blue)
[![Build status](https://scrutinizer-ci.com/g/gy-mate/moodle-to-vikwikiquiz/badges/build.png?b=main)](https://scrutinizer-ci.com/g/gy-mate/moodle-to-vikwikiquiz/build-status/main)
[![Code quality](https://img.shields.io/scrutinizer/quality/g/gy-mate/moodle-to-vikwikiquiz/main)](https://scrutinizer-ci.com/g/gy-mate/moodle-to-vikwikiquiz/)
[![Type hinting used](https://img.shields.io/badge/type_hinting-used-brightgreen)](https://docs.python.org/3/library/typing.html)
[![Code style: Black](https://img.shields.io/badge/code_style-black-black.svg)](https://github.com/psf/black)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request)


## 📖 About

A CLI for converting a graded Moodle quiz saved as an HTML file to a [vik.viki quiz](https://vik.wiki/wiki/Segítség:Kvíz) wikitext.


### 📋 Features

* Imports multiple HTML files at once
* Can create a new article on [vik.wiki](https://vik.wiki/) with the generated quiz wikitext and summary pre-filled in the editor
* Can open an existing article on [vik.wiki](https://vik.wiki/) with the summary pre-filled in the editor
* Copies the generated wikitext to the clipboard
* Supports single and multiple choice questions
* Deduplicates questions with the same text
* Asks for correct answers if it can't be determined from a graded question
* Adds the only remaining correct answer automatically if it can be determined from the grade
* Formats LaTeX equations as wikitext
* Creates placeholders for illustrations


## 📥 Installation

1. [Install Homebrew](https://brew.sh/#:~:text=Install%20Homebrew)
2. Run the following command in the terminal:
  ```bash
  brew install pipx && pipx ensurepath && pipx install moodle-to-vikwikiquiz
  ```


### 🧑‍💻 Usage

```text
moodle-to-vikwikiquiz [--verbose|-v] [--new|-n] [[--grading|-g] grading_method] source_directory parent_article title
```

Parameters:
* `new`: Create a new quiz on [vik.wiki](https://vik.wiki/) by automatically opening an edit page for the new article.
* `grading_method`: `+` or `-`. See https://vik.wiki/wiki/Segítség:Kvíz#Pontozás for further info.
* `source_directory`: The absolute path of the directory where the Moodle quiz HTML files are located. 
These HTML files should contain the _Review_ page of the quizzes.
* `parent_article`: The article name of the course on [vik.wiki](https://vik.wiki/).
* `title`: How the quiz should be named on [vik.wiki](https://vik.wiki/). This usually is in the following form: 
`[course name] kvíz – [exam name]`. (The hyphen and the part after it can be omitted.) 
This might be an existing article name if the `--new` argument is not provided.

Example:
* Convert all [Elektronika alapjai](https://vik.wiki/wiki/Elektronika_alapjai) Moodle quizzes downloaded to `~/Downloads/downloaded_ELA_quizzes`:
  ```bash
  moodle-to-vikwikiquiz --new --grading + ~/Downloads/downloaded_ELA_quizzes "Elektronika alapjai" "Elektronika alapjai kvíz"
  ```

Always check the output before uploading it to [vik.wiki](https://vik.wiki/). 
Upload all images and add their filenames to the quiz manually on [vik.wiki](https://vik.wiki/).


### ⏫ Updating

Run the following command in the terminal:
```bash
pipx upgrade-all
```

If you want this to run automatically, create a cron job:

1. Open the `crontab` file:
  ```bash
crontab -e
  ```
2. Add the following line to the end of the file:
  ```bash
@daily pipx upgrade-all
  ```
  You may replace `@daily` with `@weekly` or `@monthly`.

## 📜 License

This project is licensed under the _GNU General Public License v3.0_.
See the [license](copying.txt) file (or the _GPL-3.0 license_ tab on GitHub) for its full text.