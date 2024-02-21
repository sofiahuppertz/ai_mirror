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


def add_to_db(session):

    conn = get_db()
    db = conn.cursor()

    query = session['query']
    name = session['name']
    ocupation = session['ocupation']
    email = session['email']
    if session['path'] == 'A':
        db.execute("INSERT INTO new_questions (query, name, ocupation, email) VALUES (?, ?, ?, ?)", (query, name, ocupation, email))
    elif session['path'] == 'B':
        db.execute("INSERT INTO new_answers (answer, name, ocupation, email) VALUES (?, ?, ?, ?)", (query, name, ocupation, email))
    conn.commit()
    conn.close()
    return