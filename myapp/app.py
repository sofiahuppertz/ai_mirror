from classify_conversation import classify_conversation
from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import os
from openai import OpenAI
import psycopg2
import redis
from semantic_similarity import similarity
import utils
import requests

app = Flask(__name__)

# Set session management to redis servers

app.config['SECRET_KEY'] = "secret"
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')

Session(app)

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)


# List of chatbot responses

chatbot_responses = []
chatbot_responses.append("Do you allow us to add your answer to our database for future editions of the book?")
chatbot_responses.append("Sorry I can't help you with that request.")
chatbot_responses.append("I see... Sorry we couldn't help you yet. You can add your question to the book for future editions, would you like that?")
chatbot_responses.append("How would you like your {} to appear in the book?")
chatbot_responses.append("Please add a name...")
chatbot_responses.append("Please add an ocupation or profession...")
chatbot_responses.append("Add an email to alert you when the new book edition with your added insight is published.")
chatbot_responses.append("Thank you for your contribution and for helping humans!")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



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
    
    response = ""
    placeholder = ""
    data = request.get_json()
    user_message = data.get('user_input')

    # Start the conversation
    if 'path' not in session:
        # Classify the conversation based on the user's input into 3 relevant paths: question, answer, or none of those
        session['path'] = classify_conversation(client, session, user_message)
        
        # If the user's input is a question, run a similarity search
        if (session['path'] == 'A'):

                response = similarity(client, user_message,)

                if response == "An unexpected error ocurred. Please try again later.":
                    data = utils.json_dict(response, "/", "False", "True")

                else:
                    session['question_type'] = 'A'
                    data = utils.json_dict(response, "/chatbot", "True", "False")
        # If the user's input is an answer, ask if they want to add it to the book
        elif (session['path'] == 'B'):

            response = chatbot_responses[0]

            session['question_type'] = 'B'

            data = utils.json_dict(response, "/chatbot", "True", "False")

    # Respond to different types of reuqests based on the past messages   
    elif 'question_type' in session:
            
            print(session['question_type'])
            print(user_message)

            # "Does this answer your question?"
            if session['question_type'] == 'A':
                
                # If the user is satisfied with the answer, end the conversation
                if user_message == "Yes":
                    
                    response = "&#x1F44D;"

                    data = utils.json_dict(response, "/", "False", "True")

                # If the user is not satisfied with the answer, ask if they want to add their question to the book
                else:
                    
                    response = chatbot_responses[2]

                    session['question_type'] = 'B'

                    data = utils.json_dict(response, "/chatbot", "True", "False")

            # "Would you like to add your question/answer to the book?"
            elif session['question_type'] == 'B':

                # If the user wants to add their question/answer to the book, ask for the final input
                if user_message == "Yes":
                    
                    placeholder = "question" if session['path'] == 'A' else "answer"

                    response = chatbot_responses[3].format(placeholder)

                    session['question_type'] = 'C'

                    data = utils.json_dict(response, "/chatbot", "False", "False")   

                # If the user doesn't want to add their question/answer to the book, end the conversation
                else:
                    
                    response = "&#x1F44D;"
                    
                    data = utils.json_dict(response, "/", "False", "True")

            # "How would you like your {} to appear in the book?" 
            elif session['question_type'] == 'C':
                
                # Add the user's input to the database
                
                utils.insert_to_table(f"INSERT INTO questions (question) VALUES ('{user_message}')", pprint=True)
                
                # Redirect to collect the user's information
                if 'name' not in session:
                    
                    response = chatbot_responses[4]
                    data = utils.json_dict(response, "/register_person", "False", "False")
                
                # Or end the conversation
                else:
                
                    response = chatbot_responses[7]
                    data = utils.json_dict(response, "/", "False", "True")
    # End the conversation if the user doesn't follow the conversation's flow
    else: 
        
        response = chatbot_responses[1]
        
        data = utils.json_dict(response, "/", "False", "True")
    
    # Add new messages to our history
    utils.append_to_history(session, user_message, utils.remove_link(response))
    session.modified = True

    # Return the chatbot's response
    return jsonify(data)



@app.route("/register_person", methods=["POST"])
def register_person():

    # Get the user's input and set the response based on the last request
    data = request.get_json()
    curr_request = data.get('user_input')
    previous_request = session['history'][-1]['chatbot_response']
    print(session['history'])

    if (previous_request == chatbot_responses[4]):
        session['name'] =curr_request
        response = chatbot_responses[5]
        data = utils.json_dict(response, "/register_person", "False", "False")

    elif (previous_request == chatbot_responses[5]):
        session['ocupation'] = curr_request
        response = chatbot_responses[6]
        data = utils.json_dict(response, "/register_person", "False", "False")

    else:
        session['email'] = curr_request
        response = chatbot_responses[7]
        data = utils.json_dict(response, "/", "False", "True")
        # utils.add_to_db(session)
    utils.append_to_history(session, curr_request, response)

    return jsonify(data)



@app.route("/get_data", methods=["POST"])
def get_data():

    conn, cur = utils.get_db()
    query = request.get_json()['query']
    
    cur.execute(query)
    response = cur.fetchone()      
    cur.close()
    conn.close()
  
    return jsonify({"response": response})




@app.route("/execute_query", methods=["POST"])
def execute_query():
    conn, cur = utils.get_db()
    query = request.get_json()['query']

    try:
        cur.execute(query)
        conn.commit()
        primary_key = cur.lastrowid
        print(primary_key)
    except: 
        return jsonify({"message": "Request could not be completed."})
    
    cur.close()
    conn.close()

    return jsonify({"message": "Query executed successfully.", "primary_key": primary_key})


if __name__ == '__main__':
    app.run(port=8000, debug=True)