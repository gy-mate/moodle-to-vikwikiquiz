from setuptools import setup, find_packages  # type: ignore

setup(
    name='moodle-to-vikwikiquiz',
    version='1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'moodle-to-vikwikiquiz=moodle-to-vikwikiquiz:main',
        ],
    },
)
