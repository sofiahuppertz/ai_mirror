from classify_conversation import classify_conversation
from flask import Flask, render_template, request, jsonify, session, url_for
from flask_session import Session
from models import init_db, Page, Question, Answer, Person
import os
from openai import OpenAI
import redis
from semantic_similarity import similarity
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import utils


app = Flask(__name__)

# Set session management to redis servers

app.config['SECRET_KEY'] = "secret"
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')

Session(app)

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# SQL Alchemy setup
engine = create_engine('postgresql://postgres:rosado@localhost:5432/book_db')
db_Session = sessionmaker(bind=engine)

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


init_db(engine)

@app.route("/", methods=["GET", "POST"])
def index():

    if 'page_num' not in session:
        session['page_num'] = 1

    if 'person_id' not in session:
        session['person_id'] = None
    
    return page(session['page_num'])



# ROUTE THAT DISPLAYS THE PAGE

@app.route("/page/<int:page_number>", methods=["GET", "POST"])
def page(page_number):


    print(session)
    # Clean chat history and configurations like path or question type
    utils.clean_chat(session)

    # Set the current page number in the session

    session['page_num'] = page_number

    # Change the page number based on the user's request

    if request.method == "POST":
        
        action = request.form.get('action')
        
        if action == 'next' and session['page_num'] < utils.get_row_count(db_Session, Page):
            session['page_num'] += 1
        
        elif action == 'previous' and session['page_num'] > 1:
            session['page_num'] -= 1

    # Extract the question and answer from the database
    question, answer = utils.get_question_and_answer(session['page_num'], db_Session)

    return render_template("index.html", question=question, answer=answer)



@app.route("/chatbot", methods=["POST"])
def chatbot():
    
    response = ""
    placeholder = ""
    data = request.get_json()
    input = data.get('user_input')


    print(session)
    # Start the conversation
    if 'path' not in session:
        utils.clean_chat(session)
        # Classify the conversation based on the user's input into 3 relevant paths: question, answer, or none of those
        session['path'] = classify_conversation(client, session, input, db_Session)
        # If the user's input is a question, run a similarity search
        if (session['path'] == 'A'):

                response = similarity(client, db_Session, input,)

                if response == "We couldn't find a question similar to yours... Would you like to add your question to our database?":
                    session['question_type'] = 'B'
                    data = utils.json_dict(response, "/chatbot", "True", "False")

                else:
                    session['question_type'] = 'A'
                    data = utils.json_dict(response, "/chatbot", "True", "False")
        # If the user's input is an answer, ask if they want to add it to the book
        elif (session['path'] == 'B'):

            response = chatbot_responses[0]

            session['question_type'] = 'B'

            data = utils.json_dict(response, "/chatbot", "True", "False")
            # End the conversation if the user doesn't follow the conversation's flow
        else: 
            response = chatbot_responses[1]

            data = utils.json_dict(response, "/", "False", "True")

    # Respond to different types of reuqests based on the past messages   
    elif 'question_type' in session:
            

            # "Does this answer your question?"
            if session['question_type'] == 'A':
                
                # If the user is satisfied with the answer, end the conversation
                if input == "Yes":
                    
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
                if input == "Yes":
                    
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
                db_session = db_Session()
                if session['path'] == 'A':
                    session['new_row_id'] = utils.insert_row(db_session, Question, question=input, person_id=session['person_id'])

                elif session['path'] == 'B':
                    session['new_row_id'] = utils.insert_row(db_session, Answer, answer=input, person_id=session['person_id'], page_id=session['page_num'])

                db_session.close()

                # Redirect to collect the user's information
                if session['person_id'] == None:
                    
                    response = chatbot_responses[4]
                    data = utils.json_dict(response, "/register_person", "False", "False")
                    
                # Or end the conversation
                else:
                
                    
                    response = chatbot_responses[7]
                    data = utils.json_dict(response, "/", "False", "True")
    
    # Add new messages to our history
    utils.append_to_history(session, input, utils.remove_link(response))
    session.modified = True

    # Return the chatbot's response
    return jsonify(data)





@app.route("/register_person", methods=["POST"])
def register_person():

    # Get the user's input and set the response based on the last request
    data = request.get_json()
    input = data.get('user_input')
    previous_request = session['history'][-1]['chatbot_response']

    db_session = db_Session()
    
    if (previous_request == chatbot_responses[4]):
        
        response = chatbot_responses[5]
        
        session['person_id'] = utils.insert_row(db_session, Person, name=input)
        
        if session['path'] == 'A':
            question = db_session.query(Question).get(session['new_row_id'])
            question.change_person_id(new_id=session['person_id'])
        
        elif session['path'] == 'B':
            answer = db_session.query(Answer).get(session['new_row_id'])
            answer.change_person_id(new_id=session['person_id'])
        
        
        data = utils.json_dict(response, "/register_person", "False", "False")

    elif previous_request == chatbot_responses[5]:
        
        response = chatbot_responses[6]
        
        person = db_session.query(Person).get(session['person_id'])
        person.set_occupation(input)

        data = utils.json_dict(response, "/register_person", "False", "False")

    elif previous_request == chatbot_responses[6]:
        response = chatbot_responses[7]

        person = db_session.query(Person).get(session['person_id'])
        person.set_email(input)
        
        data = utils.json_dict(response, "/", "False", "True")
    
    db_session.commit()
    
    db_session.close()
    
    utils.append_to_history(session, input, response)
    session.modified = True 
    
    return jsonify(data)



if __name__ == '__main__':
    app.run(port=8000, debug=True)