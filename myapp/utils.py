import csv
import json
import os
import psycopg2
import re
import requests

# Backend Fronted communication

def json_dict(response, next_route, buttons, reset_page):
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

    password = os.getenv("POSTGREE_KEY")
    conn = psycopg2.connect(
        dbname='book_db',
        user='postgres',
        password=password,
        host='localhost',
        port='5432'
    )
    cur = conn.cursor()
    return conn, cur

def get_question_and_answer(page):

    query = f"SELECT question, answer FROM book WHERE id={page}"

    # Create request headers with Content-Type as application/json
    headers = {'Content-Type': 'application/json'}

    # Convert query to JSON format
    query_json = json.dumps({'query': query})

    # Make the request with updated headers and JSON data
    response = requests.post('http://localhost:8000/get_data', data=query_json, headers=headers)
    data = response.json()
    
    if 'response' in data:
        if len(data['response']) > 0:
            question, answer = data['response']  # Extracting the first tuple
        else:
            print("No data found for the given ID.")
    else:
        print("Invalid JSON response from the server.")

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


def insert_to_table(query, pprint=False):

    # Create request headers with Content-Type as application/json
    headers = {'Content-Type': 'application/json'}

    # Convert query to JSON format
    query_json = json.dumps({'query': query})

    # Make the request with updated headers and JSON data
    response = requests.post('http://localhost:8000/execute_query', data=query_json, headers=headers)
    response = response.json()
    response = response['primary_key']
    if pprint == True:
        print(response)

    return response

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

