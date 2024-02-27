from    ast import literal_eval
import  numpy as np
from    os import remove
from    pandas import read_csv
import  utils



# Global variables

embedding_model = "text-embedding-3-large"

datafile_path = "static/text_3_large_embeddings.csv"

CHATBOT_RESPONSE = (
    "Your instructions is to provide the user with the following info :\n"
    "You will be given a Question, Answer, and Page number.\n"
    "1. Greet the user and let know there is a similar question\n"
    "2. Cite the question, do not paraphrase it, and inform the page.\n"
    "3. Provide one thing the answer talks about, the most related idea of the question to the user's message. Don't provide the entire idea you choose, just mention the answer dives into that topic.\n"
    "Your response cannot surpass 70 tokens.\n"
    "Here is an example of a response:\n"
    "Hello! We have a similar question: 'JOB SEARCH AND HIRING BECOMES A SCIENCE?' on page 37, discussing AI's role in hiring.\n"
    "For reference:\n"
    "Question: \"\"{question}\"\".\n"
    "Answer: \"\"{answer}\"\".\n"
    "Page: \"\"{page}\"\".\n"
)


# Load dataframe

def load_dataframe():

    utils.export_to_csv("SELECT * FROM questions")
    dataframe = read_csv('temp.csv')    
    remove('temp.csv')

    return dataframe


# Cosine similarity

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# Search for similar questions

def similarity_search(client, new_question, n=1, pprint=False):
    
    new_question_embedding = utils.get_embedding(client, new_question, model=embedding_model)

    df = read_csv(datafile_path)

    df['embedding'] = df.embedding.apply(literal_eval).apply(np.array)

    df['similarity'] = df.embedding.apply(lambda x: cosine_similarity(x, new_question_embedding))

    results = (
        df.sort_values("similarity", ascending=False)
    )

    if pprint:
        print(results.head(n))

    
    results = np.array(results['question'].head(n))

    return results


# Function to get message with most similar question

def similarity(client, user_message):

    try:    
        question = similarity_search(client, user_message, 1, False)
        if question is None:
            raise ValueError("Question is none")
        
        conn, cur = utils.get_db() 
        cur.execute("SELECT * FROM book WHERE question=%s", (question[0],))
        result = cur.fetchone()
        cur.close()
        conn.close()
        if result is None:
            raise ValueError("Result is none")
        
        answer = result[2]
        page = result[0]
        
        context = CHATBOT_RESPONSE.format(question=question, answer=answer, page=page)
        message = [{'role': 'system', 'content': context}, {'role': 'user', 'content': user_message}]
        response = utils.get_text_response(client, message)
        
        response += " "
        response += f'<a href="#" id="page-link" data-page-number="{page}">Check page here.</a>'
        response += " Does this answer your question?"
            
    except ValueError as e:
        print(e)
        response = "An unexpected error ocurred. Please try again later."
    
    return response


# Keep this function for later 

def generate_embeddings(client):

    # Setup question list 
    df = load_dataframe()
    df['combined'] = (
        "Question: " + df.question.str.strip() + "; Answer: " + df.answer.str.strip()
    )

    # Encode questions

    df['embedding'] = df.combined.apply(lambda x: utils.get_embedding(client, x=embedding_model))

    df = df.drop(columns=['combined'])

    # Save embeddings to file
    
    df.to_csv(datafile_path)

    return
