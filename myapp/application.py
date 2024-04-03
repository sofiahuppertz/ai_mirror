import boto3
import chatbot_logic
from chatbot_reponses import chatbot_responses
from flask import Flask, render_template, request, jsonify, session, url_for, redirect
from flask_session import Session
from models import init_db, Page, Person
from openai import OpenAI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import utils


# SESSION AWS

botoSession = boto3.Session()
region_name = "us-east-1"

# SESSION FLASK

application = Flask(__name__)
flask_session_key = utils.get_secret(botoSession, "ai-mirror-flask-session", region_name)
application.config['SECRET_KEY'] = flask_session_key
application.config['SESSION_TYPE'] = 'filesystem'
Session(application)


# SESSION API OPENAI

api_key = utils.get_secret(botoSession, "ai-mirror-openai", region_name)
client = OpenAI(api_key=api_key)


# SESSION SQLALCHEMY

db = utils.get_secret(botoSession, "ai-mirror-db-url", region_name)
engine = create_engine(db)
db_Session = sessionmaker(bind=engine)
init_db(engine)


# ROUTES

@application.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



@application.route("/", methods=["GET", "POST"])
def index():

    session.setdefault('page_num', 1)

    return page(session['page_num'])



@application.route("/cover", methods=["GET"])
def cover():
    session['page_num'] = -3
    return render_template("cover.html")


@application.route("/author_bio", methods=["GET"])
def author_bio():
    session['page_num'] = -2
    return render_template("author_bio.html")


@application.route("/copyright", methods=["GET"])
def copyright():
    session['page_num'] = -1
    return render_template("copyright.html")


@application.route("/note_to_experts", methods=["GET"])
def note_to_experts():
    session['page_num'] = 0
    return render_template("note_to_experts.html")



# ROUTE THAT DISPLAYS THE PAGE

@application.route("/page/<string:page_number>", methods=["GET", "POST"])
def page(page_number):

    try:
        page_number = int(page_number)
    except ValueError:
        return jsonify({'error': 'Invalid request'}), 400
    # Set the current page number in the session
    total_pages = utils.get_row_count(db_Session, Page)

    if utils.isValidPage(page_number, total_pages):
        
        session['page_num'] = page_number

        session.modified = True

    # Change the page number based on the user's request

    if request.method == "POST":
        
        action = request.form.get('action')
        

        if action not in ['previous', 'next']:
            return jsonify({'error': 'Invalid request'}), 400
        
        if 'page_num' not in session:
                session['page_num'] = 1
        if action == 'next' and session['page_num'] < total_pages:

            session['page_num'] += 1
        
        elif action == 'previous' and session['page_num'] > -3:

            session['page_num'] -= 1

        session.modified = True

    # Redirect to the appropriate page
    if session['page_num'] == 0:
        return redirect(url_for('note_to_experts'))
    elif session['page_num'] == -1:
        return redirect(url_for('copyright'))
    elif session['page_num'] == -2:
        return redirect(url_for('author_bio'))
    elif session['page_num'] <= -3:
        return redirect(url_for('cover'))
        
    # Extract the question and answer from the database
    question, answer = utils.get_question_and_answer(session['page_num'], db_Session)
    answer = answer.split('\n')
    answer = '</p><p>'.join(answer)

    return render_template("index.html", question=question, answer=answer, page=session['page_num'])



# ROUTE THAT HANDLES THE CHATBOT


@application.route("/chatbot", methods=["POST"])
def chatbot():
    
    # Input validation
    
    data = request.get_json()
    
    if 'user_input' not in data:
        return jsonify({'error': 'Invalid request'}), 400
    
    input = data.get('user_input')

    # Make sure session['person_id'] is set to none if it doesn't exist (We need this variable to store other rows)

    session.setdefault('person_id', None)
    
    # Start the conversation
    if 'path' not in session:

        return chatbot_logic.handle_first_response(client, session, input, db_Session)
    
    elif 'question_type' in session:
    
        return chatbot_logic.handle_next_response(session, input, db_Session)
    
    else :
    
        return chatbot_logic.handle_invalid_response(session)



# ROUTE THAT HANDLES REGISTRATION OF PEOPLE


@application.route("/register_person", methods=["POST"])
def register_person():

    # Get the user's input and set the response based on the last request
    data = request.get_json()

    if 'user_input' not in data or 'history' not in session or 'person_id' not in session : 
        return jsonify({'error': 'Invalid request'}), 400
    
    input = data.get('user_input')
    
    
    previous_request = session['history'][-1]['chatbot_response']

    db_session = db_Session()
    
    # "Please add a name..."
    if (previous_request == chatbot_responses[4]):
        
        # Insert person's name to a new row in People table, store the id of that row
        session['person_id'] = utils.insert_row(db_session, Person, name=input)
        session.modified = True

        # Connect the id of this person to the question/answer they made
        utils.connect_to_person_id(session, db_session)

        dict = chatbot_logic.prepare_json(session, input, chatbot_responses[5], None, "/register_person", "False", "False")
    
    # "Please add an ocupation or profession..."
    elif previous_request == chatbot_responses[5]:

        if session['person_id'] == None:
            return jsonify({'error': 'Invalid request'}), 400
        utils.add_person_data(session['person_id'], db_session, "set_occupation", input)
        
        dict = chatbot_logic.prepare_json(session, input, chatbot_responses[6], None, "/register_person", "False", "False")

    # "Add an email to alert you when the new book edition with your added insight is published."
    else :
        if session['person_id'] == None:
            return jsonify({'error': 'Invalid request'}), 400
        
        utils.add_person_data(session['person_id'], db_session, "set_email", input)
        
        dict = chatbot_logic.prepare_json(session, input, chatbot_responses[7], None, "/", "False", "True")
    
    db_session.close()
    
    return jsonify(dict)


# ROUTE THAT HANDLES THE RESET OF THE CHAT

@application.route("/reset_chat", methods=["POST"])
def reset_chat():

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
    return jsonify({"response": "Chat reset"})



# ROUTE THAT PASSES HISOTRY OF THE CHAT TO THE FRONTEND

@application.route("/get_previous_chat", methods=["POST"])
def get_previous_chat():
    if 'history' in session:
        history = session['history']
        return jsonify({"response": history})
    else:
        return jsonify({"response": None})


if __name__ == '__main__':
    #application.run(host='0.0.0.0', port=5000)
    application.run(port=8000 ,debug=True)
