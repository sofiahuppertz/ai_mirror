import re
import csv
import sqlite3

# Backend Fronted communication

def create_data_dict(response, next_route, buttons, reset_page):
    dict = {
        "server_response" : response,
        "route": next_route,
        "buttons": buttons,
        "reset_page": reset_page
    }
    return dict

def remove_link(html_string):
    pattern = r'<a[^>]*>(.*?)</a>'
    return re.sub(pattern, '', html_string)


# Session utils

def clean_chat(session):
    if 'path' in session:
        session.pop('path')
    if 'question_type' in session:
        session.pop('question_type')
    if 'history' in session:
        session.pop('history')
    if 'query' in session:
        session.pop('query')
    if 'question_type' in session:
        session.pop('question_type')
    session.modified = True
    return



def append_to_history(session, user_message, chatbot_response):
    if 'history' not in session:
        session['history'] = []
    session['history'].append({
        'chatbot_response' : chatbot_response,
        'user_message' : user_message
    })
    session.modified = True
    return

# Database utils

def get_db():
    conn = sqlite3.connect('../mydatabase/questions.db')
    db = conn.cursor()
    return conn, db

def get_question_and_answer(page):
    conn, db = get_db()
    question = db.execute("SELECT question FROM questions WHERE id=?", (page,)).fetchone()
    if question is not None:
        question = question[0]
    answer = db.execute("SELECT answer FROM questions WHERE id=?", (page,)).fetchone()
    if answer is not None:
        answer = answer[0]
    conn.close()
    return question, answer


def export_to_csv(string):
    conn, db = get_db()
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

    conn, db = get_db()

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

# OpenAI utils

def get_json_response(client, model, messages):
    
    response = client.chat.completions.create(
        model=model,
        response_format={ "type": "json_object" },
        messages=messages,
        temperature=0.5,
    )
    
    return response.choices[0].message.content


def get_text_response(client, messages):
    
    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=messages,
        max_tokens=70,
        temperature=0,
    )
    
    return response.choices[0].message.content


def get_embedding(client, text: str, model):

    text = text.replace("\n", " ")
    
    response = client.embeddings.create(input=[text], model=model)

    return response.data[0].embedding
