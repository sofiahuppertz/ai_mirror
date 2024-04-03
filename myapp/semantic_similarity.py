from    ast import literal_eval
from chatbot_reponses import chatbot_responses
from models import Page
import  numpy as np
from    os import remove
import pandas as pd
import  utils
from    sqlalchemy.orm import Session



# Global variables

embedding_model = "text-embedding-3-large"

datafile_path = "static/text_3_large_embeddings.csv"


# Load dataframe

def load_dataframe(Session):

    utils.export_to_csv(Session)
    dataframe = pd.read_csv('temp.csv')    
    remove('temp.csv')

    return dataframe


# Cosine similarity

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# Search for similar questions

def similarity_search(client, new_question, n=1, pprint=False):
    
    new_question_embedding = utils.get_embedding(client, new_question, model=embedding_model)

    df = pd.read_csv(datafile_path)

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

def similarity(client, Session, user_message):

    try:    
        question = similarity_search(client, user_message, 1, False)
        if question is None:
            raise ValueError("Question is none")
        
        session = Session()

        page = session.query(Page).filter(Page.question == question[0]).first()
        
        if page is None:
            raise ValueError("Result is none")
        
        page = page.id

        response = f"Hello! We have a similar question: \"{question[0]} \" You can check the answer "
        response += f'<a href="#" id="page-link" data-page-number="{page}">here</a>'
        response += ". Does this answer your question?"
            
    except ValueError as e:
        print(e)
        response = chatbot_responses[8]
    
    return response


# Keep this function for later 

def generate_embeddings(db_Session, client):

    # Setup question list 
    with db_Session() as session:
        data = session.query(Page).all()
        df = pd.DataFrame([(d.question, d.answer) for d in data], columns=['question', 'answer'])
    df['combined'] = (
        "Question: " + df.question.str.strip() + "; Answer: " + df.answer.str.strip()
    )

    # Encode questions

    df['embedding'] = df.combined.apply(lambda x: utils.get_embedding(client, x, model=embedding_model))

    df = df.drop(columns=['combined'])

    # Save embeddings to file
    
    df.to_csv(datafile_path)

    return


