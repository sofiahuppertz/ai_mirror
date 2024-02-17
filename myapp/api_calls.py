

def get_json_from_gpt(client, model, messages):
    response = client.chat.completions.create(
        model=model,
        response_format={ "type": "json_object" },
        messages=messages,
        temperature=0.5,
    )
    return response.choices[0].message.content

def get_text_response(client, messages):
    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=messages,
        max_tokens=70,
        temperature=0,
    )
    return response.choices[0].message.content

