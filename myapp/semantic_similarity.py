from flask import jsonify
import os
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import tables
import time


def generate_embeddings(output_queue):
    tables.export_to_csv("SELECT id, question, answer FROM questions")
    df = pd.read_csv('temp.csv')
    os.remove('temp.csv')
    df['qa'] = df['question'] + ' ' + df['answer']
    questions = df['qa'].tolist()
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    question_embeddings = model.encode(questions)
    output_queue.put((model, question_embeddings, df))
    return

def similarity_search(user_message, model, question_embeddings, df):
    
    query_embedding = model.encode(user_message)
    # Calculate cosine similarities between the query and all questions
    similarities = util.pytorch_cos_sim(query_embedding, question_embeddings)

    # Find the top-N most similar questions
    top_n = 10
    top_indices = similarities.argsort(descending=True)[:top_n]
    top_indices_list = [i for sublist in top_indices.tolist() for i in sublist]
    # Retrieve only the top-N similar questions
    #similar_questions = [questions[i] for i in top_indices_list[:top_n]]
    similar_questions = [df['question'].iloc[i] for i in top_indices_list[:top_n]]
    return similar_questions


def wait_for_output_queue(output_queue, timeout=10):
    start_time = time.time()
    while output_queue.empty():
        if time.time() - start_time > timeout:
            return jsonify({'error': 'Timeout waiting for output_queue'}), 500
        time.sleep(0.01)
    return None