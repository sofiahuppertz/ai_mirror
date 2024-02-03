from flask import Flask, render_template, request, jsonify, session
from helpers import get_db, close_connection, get_question_and_answer, format_template, get_completion_from_messages
from templates import CLASSIFICATION
import os
from openai import OpenAI
import sqlite3

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
            print("next: ", session['index']) 
        elif action == 'previous' and session['index'] > 1:
            session['index'] -= 1
            print("previous: ", session['index'])
    question, answer = get_question_and_answer(session['index'])
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