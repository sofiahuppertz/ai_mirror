import csv
import json
from models import Page
import os
import psycopg2
import re
import requests
from sqlalchemy import func


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
    if 'new_row_id' in session:
        session.pop('new_row_id')
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



def get_question_and_answer(page_id, Session):

    session = Session()

    page = session.query(Page).get(page_id)

    if page is not None:
        return page.question, page.answer
    else:
        print("No data found for the given ID.")
        return None, None


# Funtion to count rows of a table
    
def get_row_count(Session, table_class):

    # Open secure connection
    session = Session()
    
    row_count = session.query(func.count(table_class.id)).scalar()
    
    return row_count


def export_to_csv(Session):

    session = Session()

    pages = session.query(Page).all()

    with open('pages.csv', 'w', newline='') as f:

        writer = csv.writer(f)
        column_names = [column.name for column in Page.__table__.column]
        writer.writerow(column_names)

        for page in pages:
            writer.writerow([getattr(page, column.name) for column in Page.table.column])

    session.close()


def insert_row(Session, table_class, input, person_id):

    session = Session()

    new_row = table_class(input, person_id)

    session.add(new_row)

    session.commit()

    session.close()
    
    return new_row.id


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

