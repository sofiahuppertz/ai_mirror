from api_calls import get_json_from_gpt, get_text_response
from semantic_similarity import similarity_search
from tables import get_question_and_answer, get_db
from templates import CLASSIFICATION, MOST_SIMILAR_QA, MOST_SIMILAR_QA_FINAL, DEFINE_PREVIOUS_QUESTION
import json

def get_conversation_path(client, session, user_message):
    question, answer = get_question_and_answer(session['index'])
    context = CLASSIFICATION["content"].format(question=question, answer=answer)
    messages = [{'role': 'system', 'content': context}, {'role': 'user', 'content': user_message}]
    response = get_json_from_gpt(client, "gpt-3.5-turbo-0125", messages)
    print(response)
    response = json.loads(response)
    response = response['response']
    return response 

def get_most_similar_question(client, user_message, model, question_embeddings, df):
    similar_questions = similarity_search(user_message, model, question_embeddings, df)
    questions = ""
    for i, question in enumerate(similar_questions):
        questions += f"{i+1}. {question}\n"
    print(questions)
    context = MOST_SIMILAR_QA["content"].format(questions=questions)
    messages = [{'role': 'system', 'content': context}, {'role': 'user', 'content': user_message}]
    print(messages)
    response = get_json_from_gpt(client, "gpt-4-0125-preview", messages) #gpt-4-0125-preview is better but it's not working 
    response = json.loads(response)
    print("Response from get_json_from_gpt: ")
    print(response)
    print("-" * 50)
    #check if it's an empty object
    if response == {}:    
        response = "Hello! We haven't found a similar question at this moment. Would you like to add your question to the book for future editions?"
    else:
        page_idx = response['response']
        print("page_idx: ", page_idx)
        print("-" * 50)
        question = similar_questions[int(page_idx)-1]
        print("Final question: ", question)
        print("-" * 50)
        conn = get_db()
        db = conn.cursor()
        result = db.execute("SELECT * FROM questions WHERE question=?", (question,)).fetchone()
        conn.close()
        print("Result from database: ", result)
        print("-" * 50)
        if result is not None:
            answer = result[2]
            page_idx = result[0]
            context = MOST_SIMILAR_QA_FINAL.format(question=question, answer=answer, page=page_idx)
            message = [{'role': 'system', 'content': context}, {'role': 'user', 'content': user_message}]
            print(message)
            print("-" * 50)
            response = get_text_response(client, message)
            response += " "
            response += f'<a href="#" id="page-link" data-page-number="{page_idx}">Check page here.</a>'
            response += " Does this answer your question?"
    return response


def get_question_path(client, session):
    question = session['history'][-1]['chatbot_response']
    messages = [{'role': 'system', 'content': DEFINE_PREVIOUS_QUESTION}, {'role': 'user', 'content': question}]
    print(messages)
    response = get_json_from_gpt(client, "gpt-3.5-turbo-0125", messages)
    response = json.loads(response)
    response = response['response']
    return response