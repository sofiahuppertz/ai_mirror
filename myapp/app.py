from api_calls import get_completion_from_messages
from flask import Flask, render_template, request, jsonify, session
from tables import get_db, close_connection, get_question_and_answer, export_to_csv
from templates import CLASSIFICATION
import os
from openai import OpenAI
import sqlite3
import pandas
from sentence_transformers import SentenceTransformer

#http://localhost:8000/phpliteadmin.php

app = Flask(__name__)
app.secret_key = 'secret'

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

@app.teardown_appcontext
def teardown_db(exception):
    close_connection(exception)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
def index():
    if 'index' not in session:
        session['index'] = 1 
    if request.method == "POST":
        action = request.form.get('action')
        if action == 'next' and session['index'] < 6:
            session['index'] += 1
        elif action == 'previous' and session['index'] > 1:
            session['index'] -= 1
    question, answer = get_question_and_answer(session['index'])
    export_to_csv()
    df = pandas.read_csv('questions_temp.csv')
    model = SentenceTransformer('all-MiniLM-L6-v2')
    # Generate embeddings for questions and answers
    question_embeddings = model.encode(df['Question'].tolist(), convert_to_tensor=True)
    answer_embeddings = model.encode(df['Answer'].tolist(), convert_to_tensor=True)
    # Add embeddings as new columns
    df['Question_Embeddings'] = question_embeddings.tolist()
    df['Answer_Embeddings'] = answer_embeddings.tolist()

    # Save the DataFrame with embeddings to a new CSV file
    df.to_csv('your_dataset_with_embeddings.csv', index=False)


    return render_template("index.html", question=question, answer=answer)


@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.get_json()
    user_message = data.get('client_request')
    question, answer = get_question_and_answer(session['index'])
    context = CLASSIFICATION["content"].format(question=question, answer=answer)
    messages = [{'role': 'system', 'content': context}, {'role': 'user', 'content': user_message}]
    response = get_completion_from_messages(client, messages)
    print(response)
    return jsonify({"response": "success"})

 
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)