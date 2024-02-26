from classify_conversation import classify_conversation
from flask import Flask, render_template, request, jsonify, session, url_for, redirect
import json
import os
from openai import OpenAI
from semantic_similarity import similarity
import time
import utils


#http://localhost:8000/phpliteadmin.php


app = Flask(__name__)
app.secret_key = 'secret'

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)


placeholder = ""


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# ROUTE THAT INITALIZES THE PAGE IF IT IS A NEW SESSION

@app.route("/", methods=["GET", "POST"])
def index():

    if 'page_num' not in session:
        session['page_num'] = 1
    
    return page(session['page_num'])



# ROUTE THAT DISPLAYS THE PAGE

@app.route("/page/<int:page_number>", methods=["GET", "POST"])
def page(page_number):

    # Clean chat history and configurations like path or question type

    utils.clean_chat(session)

    # Set the current page number in the session

    session['page_num'] = page_number

    # Change the page number based on the user's request

    if request.method == "POST":
        
        action = request.form.get('action')
        
        if action == 'next' and session['page_num'] < 94:
            session['page_num'] += 1
        
        elif action == 'previous' and session['page_num'] > 1:
            session['page_num'] -= 1

    # Extract the question and answer from the database
            
    question, answer = utils.get_question_and_answer(session['page_num'])

    return render_template("index.html", question=question, answer=answer)



@app.route("/chatbot", methods=["POST"])
def chatbot():
    
    data = request.get_json()
    user_message = data.get('user_input')

    #handle conversation path
    if 'path' not in session:
        session['path'] = classify_conversation(client, session, user_message)

    if (session['path'] == 'A'):
            
            response = similarity(client, user_message,)

            if response == "An unexpected error ocurred. Please try again later.":
                data = utils.create_data_dict(response, "/", "False", "True")
            
            else:
                session['question_type'] = 'A'
                data = utils.create_data_dict(response, "/handle_question", "True", "False")
    
    elif (session['path'] == 'B'):
        
        response = "Do you allow us to add your answer to our database for future editions of the book?"
        
        session['question_type'] = 'B'
        
        data = utils.create_data_dict(response, "/handle_question", "True", "False")
    
    else: 
        
        response = "Sorry I can't help you with that request."
        
        data = utils.create_data_dict(response, "/", "False", "True")
    
    utils.append_to_history(session, user_message, utils.remove_link(response))
    return jsonify(data)



@app.route("/handle_question", methods=["POST"])
def handle_question():

    response = " "
    data = request.get_json()
    user_message = data.get('button_value')

    if session['question_type'] == 'A':
        
        if user_message == "Yes":
            response = "&#x1F44D;"
            
            data = utils.create_data_dict(response, "/", "False", "True")
        
        else:
            response = "I see... Sorry we couldn't help you yet. You can add your question to the book for future editions, would you like that?"
            
            session['question_type'] = 'B'
            
            data = utils.create_data_dict(response, "/handle_question", "True", "False")
    
    if session['question_type'] == 'B':

        if user_message == "Yes":
            placeholder = "question" if session['path'] == 'A' else "answer"
            
            response = "How would you like your {} to appear in the book?".format(placeholder)
            
            data = utils.create_data_dict(response, "/colect_data", "False", "False")   
        
        else:
            response = "&#x1F44D;"
            data = utils.create_data_dict(response, "/", "False", "True")
    
    utils.append_to_history(session, user_message, response)
    return jsonify(data) 





@app.route("/colect_data", methods=["POST"])
def colect_data():
    data = request.get_json()
    user_message = data.get('user_input')
    last_request = session['history'][-1]['chatbot_response']

    if last_request == "How would you like your question to appear in the book?":
        session['query'] = user_message
        response = "Please add a name..."
        data = utils.create_data_dict(response, "/colect_data", "False", "False")
    elif (last_request == "How would you like your answer to appear in the book?"):
        session['query'] = user_message
        response = "Please add a name..."
        data = utils.create_data_dict(response, "/colect_data", "False", "False")
    elif (last_request == "Please add a name..."):
        session['name'] = user_message
        response = "Please add an ocupation or profession..."
        data = utils.create_data_dict(response, "/colect_data", "False", "False")
    elif (last_request == "Please add an ocupation or profession..."):
        session['ocupation'] = user_message
        response = "Add an email to alert you when the new book edition with your added insight is published."
        data = utils.create_data_dict(response, "/colect_data", "False", "False")
    else:
        session['email'] = user_message
        response = "Thank you for your contribution and for helping humans!"
        data = utils.create_data_dict(response, "/", "False", "True")
        utils.add_to_db(session)
    utils.append_to_history(session, user_message, response)

    return jsonify(data)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)