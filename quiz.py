import contextlib
import os
import re

from bs4 import BeautifulSoup

from grading_types import GradingType
from question import Question
from question_types import QuestionType


class Quiz:
    def __init__(self, parent_article: str, title: str, grading: GradingType | None = None):
        self.parent_article = parent_article
        self.title = title
        self.grading = grading
        
        self.questions: set[Question] = set()
    
    def __str__(self) -> str:
        text = f"{{{{Vissza | {self.parent_article}}}}}"
        text += f"""

{{{{Kvízoldal
|cím={self.title}"""
        if self.grading:
            text += f"\n|pontozás={self.grading.value}"
        text += "\n}}"
        
        for question in self.questions:
            text += f"\n\n\n{question}"
        
        return text
    
    def import_questions(self, directory: str) -> None:
        questions: list[Question] = []
        for subdir, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(subdir, file)
                with open(file_path, "r") as source_file:
                    webpage = BeautifulSoup(source_file, "html.parser")
                    
                    multichoice_questions = webpage.find_all("div", class_="multichoice")
                    for question in multichoice_questions:
                        correctly_answered: bool
                        grading_text = question.find("div", class_="grade").text
                        numbers = re.findall(r"\d+\.\d+", grading_text)
                        grade = float(numbers[0])
                        maximum_points = float(numbers[1])
                        if grade == maximum_points:
                            correctly_answered = True
                        else:
                            correctly_answered = False
                        
                        question_text = question.find("div", class_="qtext").text
                        answers = question.find("div", class_="answer")
                        answer_texts: list[str] = []
                        correct_answers: list[int] = []
                        i = 1
                        for answer in answers:
                            with contextlib.suppress(TypeError):
                                answer_texts.append(answer.find("div", class_="ml-1").text)
                                if "correct" in answer["class"]:
                                    correct_answers.append(i)
                                i += 1
                        if not correctly_answered:
                            print(f"""

Question: '{question_text}'

I see that answers {correct_answers} are correct, but this list may be incomplete because you only got {grade:g} points out of {maximum_points:g}.

The answers are:""")
                            for j, answer in enumerate(answer_texts):
                                print(f"#{j + 1}\t{answer}")
                            print()
                            while True:
                                additional_correct_answer = input(
                                    f"Please enter a missing correct answer (if there is any remaining) and press Enter: ")
                                if additional_correct_answer == "" or len(correct_answers) == len(answer_texts) - 1:
                                    break
                                correct_answers.append(int(additional_correct_answer))
                        illustration = True if question.find("img", class_="img-responsive") else False
                        questions.append(
                            Question(q_type=QuestionType.MultipleChoice, text=question_text, illustration=illustration,
                                     answers=answer_texts,
                                     correct_answers=correct_answers))
        self.questions = set(questions)
        
    def deduplicate_questions(self) -> None:
        copied_questions = list(self.questions)
        other_copied_questions = list(self.questions)
        new_questions: list[Question] = []
        with contextlib.suppress(KeyError):
            while copied_questions:
                question = copied_questions.pop()
                i = 0
                while True:
                    other_question = other_copied_questions[i]
                    if question != other_question and question.text == other_question.text:
                        for j, answer in enumerate(other_question.answers):
                            if answer not in question.answers:
                                question.answers.append(answer)
                                if j + 1 in other_question.correct_answers:
                                    question.correct_answers.append(len(question.answers))
                        other_copied_questions.remove(other_question)
                    else:
                        i += 1
                        if i >= len(other_copied_questions):
                            break
                other_copied_questions.remove(question)
                new_questions.append(question)
        self.questions = set(new_questions)
