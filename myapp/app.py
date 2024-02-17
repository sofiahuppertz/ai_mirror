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
    reset_history(session)
    reset_path(session)
    question, answer = get_question_and_answer(session['index'])
    thread = Thread(target=generate_embeddings, args=(output_queue,))
    thread.start()
    return render_template("index.html", question=question, answer=answer)


@app.route('/change_page', methods=['POST'])
def change_page():
    data = request.get_json()
    session['index'] = int(data.get('index'))
    reset_history(session)
    reset_path(session)
    return redirect(url_for('index'))


@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.get_json()
    user_message = data.get('user_input')
    buttons = "False"
    print("User message: ", user_message)  
    print("-" * 50)
    chatbot_response = " "
    if 'history' not in session:
        session['history'] = []
    #handle conversation path
    print("Session: ", session)
    if 'path' not in session:
        session['path'] = get_conversation_path(client, session, user_message)
        print("Path: ", session['path'])
        print("-" * 50)

    #handle path A
    if (session['path'] == 'A'):
            # Wait for question embeddings to be generated
            error_response = wait_for_output_queue(output_queue)
            if error_response is None:
                model, question_embeddings, df = output_queue.get()
                chatbot_response = get_most_similar_question(client, user_message, model, question_embeddings, df)
                buttons = "True"
                append_to_history(session, user_message, remove_link(chatbot_response))

    return jsonify({"server_response": chatbot_response, "buttons": buttons})

@app.route("/handle_question", methods=["POST"])
def handle_question():
    chatbot_response = " "
    data = request.get_json()
    user_message = data.get('button_value')
    print(user_message)
    print(session['history'])
    # Define based on history wether the reply is to 1) Ask if answer was helpful or 2) Ask if user wants to add question to book.
    response = get_question_path(client, session)
    print("response: ", response) 
    if response == 'A':
        if user_message == "Yes":
            #Greet and finish conversation
            chatbot_response = "&#x1F44D;"
            buttons = "False"
            end_chat = "True"
        else:
            # Ask if user would like to add question to book
            chatbot_response = "I see... Sorry we couldn't help you yet. You can add your question to the book for future editions, would you like that?"
            buttons = "True"
            end_chat = "False"
    if response == 'B':
        if user_message == "Yes":
            chatbot_response = "Proceed to adding question to database ..."
            buttons = "False"
            end_chat = "False"
        else:
            chatbot_response = "Greet and finish conversation..."
            buttons = "False"
            end_chat = "True"
    append_to_history(session, user_message, chatbot_response)
    if (end_chat == "True"):
        reset_path(session)
        reset_history(session)
    return jsonify({"server_response": chatbot_response, "buttons": buttons, "end_chat": end_chat}) 


@app.route("/end_chat", methods=["POST"])
def end_chat():
    reset_history(session)
    reset_path(session)
    return jsonify({'redirect': url_for('index')})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)