
def reset_path(session):
    if 'path' in session:
        session.pop('path')
    session.modified = True
    return

def reset_history(session):
    if 'history' in session:
        session.pop('history')
    session.modified = True
    return

def append_to_history(session, user_message, chatbot_response):
    if 'history' not in session:
        session['history'] = []
    session['history'].append({
        'user_message' : user_message,
        'chatbot_response' : chatbot_response
    })
    session.modified = True
    return

def create_data_dict(response, next_route, buttons, reset_page):
    dict = {
        "server_response" : response,
        "route": next_route,
        "buttons": buttons,
        "reset_page": reset_page
    }
    return dict