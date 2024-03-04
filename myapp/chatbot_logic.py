from chatbot_reponses import chatbot_responses
from classify_conversation import classify_conversation
from models import Question, Answer
from semantic_similarity import similarity
import utils

def prepare_json(session, input, response, question_type, next_route, buttons, reset_page):
    
    if question_type and session:
        session['question_type'] = question_type
    
    utils.append_to_history(session, input, utils.remove_link(response))
    session.modified = True

    dict = {
        "server_response" : response,
        "route": next_route,
        "buttons": buttons,
        "reset_page": reset_page
    }
    return dict


def register_person(session, input, question_type):
        
        if session['person_id'] == None:
            return prepare_json(session, input, chatbot_responses[4], question_type, "/register_person", "False", "False") 
    
        else:
            return prepare_json(session, input, chatbot_responses[7], None, "/", "False", "True")



def handle_first_response(client, session, input, db_Session ):
    
    session['path'] = classify_conversation(client, session, input, db_Session)

    if session['path'] == 'A':
        response = similarity(client, db_Session, input)

        if response == chatbot_responses[8]:
            return prepare_json(session, input, response, 'B', "/chatbot", "True", "False")        
        else:
            return prepare_json(session, input, response, 'A', "/chatbot", "True", "False")

    elif session['path'] == 'B' :
        return prepare_json(session, input, chatbot_responses[0], 'B', "/chatbot" , "True", "False")

    else:
        return handle_invalid_response(session)
    

def handle_next_response(session, input, db_Session):

    question_type = session['question_type']

    # "Does this answer your question?"
    if question_type == 'A':
        
        if input == "No":
            return prepare_json(session, input, chatbot_responses[2], 'B', "/chatbot", "True", "False")
    
    # "Would you like to add your question/answer to the book?"
    elif question_type == 'B':

        if  input == "Yes":
            placeholder = "question" if session['path'] == 'A' else "answer"
            return prepare_json(session, input, chatbot_responses[3].format(placeholder), 'C', "/chatbot", "False", "False")
    # "How would you like your question/answer to appear in the book?" 
    elif question_type == 'C':

        # Add to database
        db_session = db_Session()
        
        if session['path'] == 'A':
            if 'new_row_id' not in session:
                
                session['new_row_id'] = utils.insert_row(db_session, Question, question=input, person_id=session['person_id'])
                db_session.close()
                return prepare_json(session, input, chatbot_responses[10], 'D', "/chatbot", "True", "False")
            
            else:
                
                question = db_session.query(Question).get(session['new_row_id'])
                question.add_answer(input)
                db_session.commit()
                db_session.close()
                return register_person(session, input, question_type)
            
        elif session['path'] == 'B':
            session['new_row_id'] = utils.insert_row(db_session, Answer, answer=input, person_id=session['person_id'], page_id=session['page_num'])
        
            db_session.close() 
        
            return register_person(session, input, question_type)
    
    # "Would you like to add an answer?"
    elif question_type == 'D':
        
        if input == "Yes":
            return prepare_json(session, input, chatbot_responses[3].format("answer"), 'C', "/chatbot", "False", "False")
        else:
            return register_person(session, input, question_type)

    return prepare_json(session, input, chatbot_responses[9], None, "/", "False", "True")



def handle_invalid_response(session):
    return prepare_json(session, input, chatbot_responses[1], None, "/", "False", "True")


