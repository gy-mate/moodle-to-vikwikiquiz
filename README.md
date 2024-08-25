# 🎓 moodle-to-vikwikiquiz

![Lines of code](https://img.shields.io/badge/lines_of_code-900+-blue)
[![Build status](https://scrutinizer-ci.com/g/gy-mate/moodle-to-vikwikiquiz/badges/build.png?b=main)](https://scrutinizer-ci.com/g/gy-mate/moodle-to-vikwikiquiz/build-status/main)
[![Code quality](https://img.shields.io/scrutinizer/quality/g/gy-mate/moodle-to-vikwikiquiz/main)](https://scrutinizer-ci.com/g/gy-mate/moodle-to-vikwikiquiz/)
[![Type hinting used](https://img.shields.io/badge/type_hinting-used-brightgreen)](https://docs.python.org/3/library/typing.html)
[![Code style: Black](https://img.shields.io/badge/code_style-black-black.svg)](https://github.com/psf/black)

[![Recent activity](https://img.shields.io/github/commit-activity/m/gy-mate/moodle-to-vikwikiquiz)](https://github.com/gy-mate/moodle-to-vikwikiquiz/commits/main/)
![Commits since latest release](https://img.shields.io/github/commits-since/gy-mate/moodle-to-vikwikiquiz/latest)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request)


## 📖 About

A CLI for converting graded [Moodle quizzes](https://docs.moodle.org/404/en/Quiz_activity) saved as HTML files to a [vik.viki quiz](https://vik.wiki/Segítség:Kvíz) wikitext.


## 📥 Installation

### ✨ Easy

1. [Install `pipx`](https://pipx.pypa.io/stable/#install-pipx)
1. _If using Linux: [follow these steps](https://github.com/asweigart/pyperclip/blob/master/docs/index.rst#not-implemented-error)._
1. Run the following command in the terminal:

    ```bash
    pipx install moodle-to-vikwikiquiz
    ```


### 🛠️ Executable `zipapp`

1. Download the `.pyz` file of the latest release from [here](https://github.com/gy-mate/moodle-to-vikwikiquiz/releases/latest).
1. Run the following commands in the terminal:

    ```bash
    chmod +x moodle-to-vikwikiquiz_x.x.x.pyz
    ./moodle-to-vikwikiquiz_x.x.x.pyz [parameters]
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

Always check and correct the output before submitting it to the wiki!
This includes uploading all images and adding their filenames to the quiz manually.


### 📋 Features

* Imports multiple HTML files at once (recursively, if desired)
* Supports true or false, single and multiple choice questions
* Opens an existing article or creates a new one on [vik.wiki](https://vik.wiki/) with the edit summary pre-filled
* Formats LaTeX equations as wikitext
* Adds the only remaining correct answer automatically if it can be determined from the grade
* Asks for correct answers if it can't be determined from a graded question
* Deduplicates questions with the same text
* Prepares illustrations for batch upload
    * If they are unavailable: creates placeholders for them
* Copies the generated wikitext to the clipboard


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

### ⌨️ Developing

After you make changes to the Python codebase, please check whether the supported minimum Python version has changed. 
Run the following command in the terminal:

```bash
vermin --backport argparse --backport enum --backport typing_extensions --eval-annotations .
```

If it has changed, update [`pyproject.toml`](pyproject.toml) accordingly.

### 🏗️ Building

- Wheels (`.whl`):
    1. Install `build`:
        ```bash
        python3 -m pip install --upgrade pip
        pip install build
        ```
    1. Create the wheels:
        ```bash
        python3 -m build
        ```

- `zipapp` (`.pyz`):
    1. [Install `pipx`](https://pipx.pypa.io/stable/#install-pipx)
    1. Install `shiv`:
        ```bash
        pipx install shiv
        ```
    1. Create the executable:
        ```bash
        shiv --entry-point moodle_to_vikwikiquiz.main:main --output-file moodle-to-vikwikiquiz.pyz --reproducible .
        ```


## 📜 License

This project is licensed under the _GNU General Public License v3.0_.
See the [license](copying.txt) file (or the _GPL-3.0 license_ tab on GitHub) for its full text.
