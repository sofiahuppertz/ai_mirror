
CLASSIFICATION = {
    "role": "system",
    "content": (
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
}

MOST_SIMILAR_QA = {
    "role": "system",
    "content": (
        "Your task is to determine which of the 10 following AI-related questions is most related or semantically similar to the user_message."
        "The idea is to give the user a similar or identical topic we have in the book.\n"
        "When you determine which is most similar, respond with the corresponding number (e.g., 1, 2, 3, etc...) "
        "Ensure your response is in JSON format with the key 'response' and the value being the determined number (e.g., {{\"response\": 1}})."
        "The user_message might be asking about A.I without mentioning it explicitly.\n"
        "IMPORTANT: Only if there are no questions, respond with an empty JSON object.\n"
        "For reference:\n"
        "Here are the questions:\n"
        "{questions}\n"
    )
}

MOST_SIMILAR_QA_FINAL = (
    "Your instructions is to provide the user with the following info :\n"
    "You will be given a Question, Answer, and Page number.\n"
    "1. Greet the user and let know there is a similar question\n"
    "2. Cite the question EXACTLY how it is provided and inform the page.\n"
    "3. Provide one thing the answer talks about, the most related idea of the question to the user's message. Don't provide the entire idea you choose, just mention the answer dives into that topic.\n"
    "YOUR RESPONSE CAN'T SURPASS 70 TOKENS.\n"
    "Here is an example of a response:\n"
    "Hello! We have a similar question: 'JOB SEARCH AND HIRING BECOMES A SCIENCE?' on page 37, discussing AI's role in hiring.\n"
    "For reference:\n"
    "Question: \"\"{question}\"\".\n"
    "Answer: \"\"{answer}\"\".\n"
    "Page: \"\"{page}\"\".\n"
)

DEFINE_PREVIOUS_QUESTION = (
    "Your task is to classify a given user message within 2 categrories:\n"
    "A) The user is asking \"Does this answer your question?\".\n"
    "B) The user is proposing you to add your question to the book.\n"
    "IMPORTANT: The response should be in JSON with the key response and the value being the letter (e.g., {{\"response\": \"A\"}}).\n"
)
