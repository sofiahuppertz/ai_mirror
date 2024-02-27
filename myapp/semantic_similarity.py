from    ast import literal_eval
import  numpy as np
from    os import remove
from    pandas import read_csv
import  utils



# Global variables

embedding_model = "text-embedding-3-large"

datafile_path = "static/text_3_large_embeddings.csv"


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
        
        page = result[0]

        response = f"Hello! We have a similar question: {question[0]} on page {page},  "
        response += f'<a href="#" id="page-link" data-page-number="{page}">check page here.</a>'
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
