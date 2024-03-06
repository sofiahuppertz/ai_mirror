
// FUNCTION TO APPEAR MESSAGES IN CHAT

export function send_message(message, className){
    let chatMessageDiv = document.createElement('div');
    chatMessageDiv.innerHTML = message;
    chatMessageDiv.className = className;
    let chatHistory = document.querySelector('#chat-history');
    chatHistory.appendChild(chatMessageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

//FUCNTION TO SEND DATA TO SERVER

export function postData(route, data) {

    console.log('clearing local storage');
    localStorage.removeItem('currentFunction');
    localStorage.removeItem('nextRoute');


    console.log('route inside PostData: ', route)
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
    console.log('add_previous_chat');
    fetch('/get_previous_chat', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        let history = data['response'];
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