# moodle-to-vikwikiquiz

![Lines of code](https://img.shields.io/badge/lines_of_code-600+-blue)
[![Build status](https://scrutinizer-ci.com/g/gy-mate/moodle-to-vikwikiquiz/badges/build.png?b=main)](https://scrutinizer-ci.com/g/gy-mate/moodle-to-vikwikiquiz/build-status/main)
[![Code quality](https://img.shields.io/scrutinizer/quality/g/gy-mate/moodle-to-vikwikiquiz/main)](https://scrutinizer-ci.com/g/gy-mate/moodle-to-vikwikiquiz/)
[![Type hinting used](https://img.shields.io/badge/type_hinting-used-brightgreen)](https://docs.python.org/3/library/typing.html)
[![Code style: Black](https://img.shields.io/badge/code_style-black-black.svg)](https://github.com/psf/black)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request)


## 📖 About

A CLI for converting graded [Moodle quizzes](https://docs.moodle.org/404/en/Quiz_activity) saved as HTML files to a [vik.viki quiz](https://vik.wiki/wiki/Segítség:Kvíz) wikitext.


## 📥 Installation

### ✨ Easy

1. [Install `pipx`](https://pipx.pypa.io/stable/#install-pipx)
1. If using Linux: follow [these steps](https://github.com/asweigart/pyperclip/blob/master/docs/index.rst#not-implemented-error).
1. Run the following command in the terminal:

    ```bash
    pipx install moodle-to-vikwikiquiz
    ```


### 🛠️ Executable `zipapp`

1. Download the `.pyz` file of the latest release from [here](https://github.com/gy-mate/moodle-to-vikwikiquiz/releases/latest).
1. Run the following command in the terminal:

    ```bash
    python3 moodle-to-vikwikiquiz.pyz source_directory
    ```


## 🧑‍💻 Usage

```text
moodle-to-vikwikiquiz [--verbose|-v] [--new|-n] [--recursive|-r] source_path
```

Parameters:
* `--new`: Create a new quiz on [vik.wiki](https://vik.wiki/) by automatically opening an edit page for the new article.
* `--recursive`: Import HTML files from the current directory recursively.
* `source_path`: The absolute or relative path of the file or directory where the Moodle quiz HTML files are located.
  These HTML files should contain the _Review_ page of the quizzes.

Always check the output before uploading it to [vik.wiki](https://vik.wiki/). 
Upload all images and add their filenames to the quiz manually on [vik.wiki](https://vik.wiki/).


### 📋 Features

* Imports multiple HTML files at once (recursively, if desired)
* Can open an existing article or create a new one on [vik.wiki](https://vik.wiki/) with the edit summary pre-filled
* Copies the generated wikitext to the clipboard
* Supports true or false, single and multiple choice questions
* Deduplicates questions with the same text
* Asks for correct answers if it can't be determined from a graded question
* Adds the only remaining correct answer automatically if it can be determined from the grade
* Formats LaTeX equations as wikitext
* Creates placeholders for illustrations


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

1. Add this line to the beginning of the file:
    ```bash
    PATH=~/.local/bin
    ```
    If there is already a line beginning with `PATH=`, add `:~/.local/bin` to the end of it.

1. Add the following line to the end of the file:
    ```bash
    @daily		pipx upgrade-all
    ```
   You may replace `@daily` with `@weekly` or `@monthly`.


## 🧑‍💻 Development

### 🏗️ Building

- Wheels (`.whl`):
    ```bash
    python -m build
    ```

- `zipapp` (`.pyz`):
    ```bash
    shiv --entry-point moodle_to_vikwikiquiz.main:main --output-file moodle-to-vikwikiquiz.pyz --reproducible .
    ```


## 📜 License

This project is licensed under the _GNU General Public License v3.0_.
See the [license](copying.txt) file (or the _GPL-3.0 license_ tab on GitHub) for its full text.