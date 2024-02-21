from flask import Flask, render_template, request, jsonify, session, url_for, redirect
import json
from helpers import *
import os
from openai import OpenAI
from queue import Queue
from threading import Thread
import time



#http://localhost:8000/phpliteadmin.php

app = Flask(__name__)
app.secret_key = 'secret'

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

output_queue = Queue()
placeholder = ""

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
        if action == 'next' and session['index'] < 94:
            session['index'] += 1
        elif action == 'previous' and session['index'] > 1:
            session['index'] -= 1
    reset_chatbot_info(session)
    question, answer = get_question_and_answer(session['index'])
    thread = Thread(target=generate_embeddings, args=(output_queue,))
    thread.start()
    return render_template("index.html", question=question, answer=answer)


@app.route('/turn_page', methods=['POST'])
def turn_page():
    data = request.get_json()
    session['index'] = int(data.get('index'))
    reset_chatbot_info(session)
    return redirect(url_for('index'))


@app.route("/reset_page", methods=["POST"])
def reset_page():
    reset_chatbot_info(session)
    return redirect(url_for('index'))


@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.get_json()
    user_message = data.get('user_input')
    #handle conversation path
    print("Session: ", session)
    if 'path' not in session:
        session['path'] = get_conversation_path(client, session, user_message)
        print("Path: ", session['path'])
        print("-" * 50)
    if (session['path'] == 'A'):
            # Wait for question embeddings to be generated
            error_response = wait_for_output_queue(output_queue)
            if error_response is None:
                model, question_embeddings, df = output_queue.get()
                response = get_most_similar_question(client, user_message, model, question_embeddings, df)
                data = create_data_dict(response, "/handle_question", "True", "False")
    elif (session['path'] == 'B'):
        response = "Do you allow us to add your answer to our database for future editions of the book?"
        data = create_data_dict(response, "/handle_question", "True", "False")
    else: 
        response = "Sorry I can't help you with that request."
        data = create_data_dict(response, "/reset_page", "False", "True")
    append_to_history(session, user_message, remove_link(response))
    return jsonify(data)

@app.route("/handle_question", methods=["POST"])
def handle_question():
    response = " "
    data = request.get_json()
    user_message = data.get('button_value')
    # Define based on history wether the reply is to 1) Ask if answer was helpful or 2) Ask if user wants to add question to book.
    response = get_question_path(client, session)
    if response == 'A':
        if user_message == "Yes":
            response = "&#x1F44D;"
            data = create_data_dict(response, "/reset_page", "False", "True")
        else:
            response = "I see... Sorry we couldn't help you yet. You can add your question to the book for future editions, would you like that?"
            data = create_data_dict(response, "/handle_question", "True", "False")
    if response == 'B':
        if user_message == "Yes":
            placeholder = "question" if session['path'] == 'A' else "answer"
            response = "How would you like your {} to appear in the book?".format(placeholder)
            data = create_data_dict(response, "/colect_data", "False", "False")   
        else:
            response = "&#x1F44D;"
            data = create_data_dict(response, "/reset_page", "False", "True")
    append_to_history(session, user_message, response)
    return jsonify(data) 


@app.route("/colect_data", methods=["POST"])
def colect_data():
    data = request.get_json()
    user_message = data.get('user_input')
    last_request = session['history'][-1]['chatbot_response']

    if last_request == "How would you like your question to appear in the book?":
        session['query'] = user_message
        response = "Please add a name..."
        data = create_data_dict(response, "/colect_data", "False", "False")
    elif (last_request == "How would you like your answer to appear in the book?"):
        session['query'] = user_message
        response = "Please add a name..."
        data = create_data_dict(response, "/colect_data", "False", "False")
    elif (last_request == "Please add a name..."):
        session['name'] = user_message
        response = "Please add an ocupation or profession..."
        data = create_data_dict(response, "/colect_data", "False", "False")
    elif (last_request == "Please add an ocupation or profession..."):
        session['ocupation'] = user_message
        response = "Add an email to alert you when the new book edition with your added insight is published."
        data = create_data_dict(response, "/colect_data", "False", "False")
    else:
        session['email'] = user_message
        response = "Thank you for your contribution and for helping humans!"
        data = create_data_dict(response, "/reset_page", "False", "True")
        add_to_db(session)
    append_to_history(session, user_message, response)

    return jsonify(data)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)