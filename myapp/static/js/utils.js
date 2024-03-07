
// FUNCTION TO APPEAR MESSAGES IN CHAT

export function send_message(message, className){
    let chatMessageDiv = document.createElement('div');
    chatMessageDiv.innerHTML = message;
    chatMessageDiv.className = className;
    let chatHistory = document.querySelector('#chat-history');
    chatHistory.appendChild(chatMessageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// FUNCTION TO CREATE TYPING INDICATOR

export function createTypingIndicator() {
    let typingIndicator = document.createElement('div');
    typingIndicator.id = 'typingIndicator';
    typingIndicator.innerHTML = '<span></span><span></span><span></span>';
    let chatHistory = document.querySelector('#chat-history');
    chatHistory.appendChild(typingIndicator);
}

//FUNNTION TO SEND DATA TO SERVER

export function postData(route, data, clearStorage=true) {

    if (clearStorage) {
        localStorage.removeItem('currentFunction');
        localStorage.removeItem('nextRoute');
    }

    return fetch(route, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
}

// FUNCTION TO APPEND PREVIOUS CHATS

export function add_previous_chat(){

    fetch('/get_previous_chat', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        let history = data['response'];
        if (history === null) {
            return;
        }
        for (let i = 0; i < history.length ; i++) {
            let user_message = history[i]['user_message'];
            let chatbot_response = history[i]['chatbot_response'];
            if (user_message)
            {
                send_message(user_message, 'user_message');
            }
            if (chatbot_response)
            {
                send_message(chatbot_response, 'chatbot_response');
            }
        }
    })
}

// FUNCTION TO CHECK INPUT ISN'T EMPTY

export function isInputNotEmpty() {

    const userInput = document.getElementById('userInput');
    if (userInput && userInput.value && userInput.value.trim() !== '') {
        return true;
    }
    
    return false;
}