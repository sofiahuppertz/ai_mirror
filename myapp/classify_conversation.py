import json
import utils

# Global variables

CLASSIFICATION = (
        "Your task is to classify user input based on a a question and answer, all delimited by: '\"\"'.\n"
        "You have to categorize the user message into one of the following options based on its content:\n"
        "A) The user is asking a different question related to Artificial Intelligence.\n"
        "B) The user is providing information to answer to the question.\n"
        "C) None of the above.\n"
        "You have to respond with the corresponding letter in uppercase (e.g., A, B, C, or D). Don't add any extra characters.\n"
        "IMPORTANT: The response should be in JSON with the key response and the value being the letter (e.g., {{\"response\": \"A\"}}).\n"
        "For reference:\n"
        "Question: \"\"{question}\"\".\n"
        "Answer: \"\"{answer}\"\".\n"
        "Please categorize the user message accordingly and respond in JSON format."
    )


#Function to classify user input

def classify_conversation(client, session, user_message, db_Session):
    
    question, answer = utils.get_question_and_answer(session['page_num'], db_Session)
    
    context = CLASSIFICATION.format(question=question, answer=answer)
    
    messages = [{'role': 'system', 'content': context}, {'role': 'user', 'content': user_message}]
    
    response = utils.get_json_response(client, "gpt-3.5-turbo-0125", messages)

    response = json.loads(response)

    response = response['response']
    
    return response 
