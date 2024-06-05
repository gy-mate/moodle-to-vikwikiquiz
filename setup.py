from setuptools import find_packages, setup  # type: ignore

setup(
    name="moodle-to-vikwikiquiz",
    description="A CLI for converting a graded Moodle quiz HTML to a vik.wiki quiz wikitext.",
    author="Máté Gyöngyösi",
    url="https://github.com/gy-mate/homebrew-moodle-to-vikwikiquiz",
    version="1.0.21",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "moodle-to-vikwikiquiz=moodle_to_vikwikiquiz.main:main",
        ],
    },
    python_requires=">=3.9",
    install_requires=[
        "beautifulsoup4",
    ],
)
