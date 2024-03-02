import csv
from models import Page, Question, Answer, Person
import re
from sqlalchemy import func


# Function to remove links 

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


# DATABASE UTILS

def get_question_and_answer(page_id, db_Session):

    db_session = db_Session()

    page = db_session.query(Page).get(page_id)

    db_session.close()

    if page is not None:
        return page.question, page.answer
    else:
        print("No data found for the given ID.")
        return None, None


# Funtion to count rows of a table
    
def get_row_count(db_Session, table_class):

    # Open secure connection
    db_session = db_Session()
    
    row_count = db_session.query(func.count(table_class.id)).scalar()

    db_session.close()
    
    return row_count


def export_to_csv(db_Session):

    db_session = db_Session()

    pages = db_session.query(Page).all()

    with open('pages.csv', 'w', newline='') as f:

        writer = csv.writer(f)
        column_names = [column.name for column in Page.__table__.column]
        writer.writerow(column_names)

        for page in pages:
            writer.writerow([getattr(page, column.name) for column in Page.table.column])

    db_session.close()


def insert_row(db_session, table_class, **kwargs):

    new_row = table_class(**kwargs)

    db_session.add(new_row)

    db_session.commit()
    
    return new_row.id

def connect_to_person_id(session, db_session):
 
    print("ID: ")
    print(session['person_id'])
    if session['path'] == 'A':
            question = db_session.query(Question).get(session['new_row_id'])
            question.change_person_id(new_id=session['person_id'])
        
    elif session['path'] == 'B':
        answer = db_session.query(Answer).get(session['new_row_id'])
        answer.change_person_id(new_id=session['person_id'])
    
    db_session.commit()


def add_person_data(person_id, db_session, method, input):
    
    person = db_session.query(Person).get(person_id)

    getattr(person, method)(input)

    db_session.commit()

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

