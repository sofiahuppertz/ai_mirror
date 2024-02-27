import re
import csv
import psycopg2

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
    pattern = r'<a[^>]*>(.*%s)</a>'
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
    conn = psycopg2.connect(
        dbname='book_db',
        user='postgres',
        password='rosado',
        host='localhost',
        port='5432'
    )
    cur = conn.cursor()
    return conn, cur

def get_question_and_answer(page):
    conn, cur = get_db()
    cur.execute("SELECT question FROM book WHERE id=%s", (page,))
    question = cur.fetchone()
    if question is not None:
        question = question[0]
    answer = cur.execute("SELECT answer FROM book WHERE id=%s", (page,))
    answer = cur.fetchone()
    if answer is not None:
        answer = answer[0]
    cur.close()
    conn.close()
    return question, answer


def export_to_csv(string):
    conn, cur = get_db()
    cur.execute(string)
    rows = cur.fetchall()
    with open('temp.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        column_names = [description[0] for description in cur.description]
        writer.writerow(column_names)
        writer.writerows(rows)
    cur.close()
    conn.close()
    return


def add_to_db(session):

    conn, cur = get_db()

    query = session['query']
    name = session['name']
    ocupation = session['ocupation']
    email = session['email']
    if session['path'] == 'A':
        cur.execute("INSERT INTO new_questions (query, name, ocupation, email) VALUES (%s, %s, %s, %s)", (query, name, ocupation, email))
    elif session['path'] == 'B':
        cur.execute("INSERT INTO new_answers (answer, name, ocupation, email) VALUES (%s, %s, %s, %s)", (query, name, ocupation, email))
    conn.commit()
    cur.close()
    conn.close()
    return

# Save for later

def create_tables():
    conn, cur = get_db()

    cur.execute("""CREATE TABLE IF NOT EXISTS persons (
        person_id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        occupation VARCHAR(100),
        email VARCHAR(100) UNIQUE
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS questions (
        question_id SERIAL PRIMARY KEY,
        question TEXT NOT NULL,
        person_id INTEGER REFERENCES persons(person_id)
    );
    """)

    cur.execute("""CREATE TABLE IF NOT EXISTS answers (
        answer_id SERIAL PRIMARY KEY,
        question_id INTEGER NOT NULL REFERENCES questions(question_id),
        answer TEXT NOT NULL,
        person_id INTEGER NOT NULL REFERENCES persons(person_id)
    );
    """)

    conn.commit()
    cur.close()
    conn.close()

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

