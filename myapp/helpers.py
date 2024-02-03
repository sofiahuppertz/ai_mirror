
from flask import g
import sqlite3


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('../mydatabase/questions.db')
    return db

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def get_question_and_answer(index):
    conn = get_db()
    db = conn.cursor()
    question = db.execute("SELECT question FROM questions WHERE id=?", (index,)).fetchone()
    if question is not None:
        question = question[0]
    answer = db.execute("SELECT answer FROM questions WHERE id=?", (index,)).fetchone()
    if answer is not None:
        answer = answer[0]
    return question, answer

def format_template(template, **kwargs):
    return template.format(**kwargs)

def get_completion_from_messages(client, messages):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content