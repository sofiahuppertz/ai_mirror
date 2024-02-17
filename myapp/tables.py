import csv
from flask import g
import sqlite3


def get_db():
    db = sqlite3.connect('../mydatabase/questions.db')
    return db

def get_question_and_answer(index):
    conn = get_db()
    db = conn.cursor()
    question = db.execute("SELECT question FROM questions WHERE id=?", (index,)).fetchone()
    if question is not None:
        question = question[0]
    answer = db.execute("SELECT answer FROM questions WHERE id=?", (index,)).fetchone()
    if answer is not None:
        answer = answer[0]
    conn.close()
    return question, answer


def export_to_csv(string):
    conn = get_db()
    db = conn.cursor()
    db.execute(string)
    rows = db.fetchall()
    with open('temp.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        column_names = [description[0] for description in db.description]
        writer.writerow(column_names)
        writer.writerows(rows)
    conn.close()
    return


