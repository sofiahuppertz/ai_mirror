
// Utils.js

function send_message(message, className){
    let chatMessageDiv = document.createElement('div');
    chatMessageDiv.innerHTML = message;
    chatMessageDiv.className = className;
    let chatHistory = document.querySelector('#chat-history');
    chatHistory.appendChild(chatMessageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}


function postData(route, data) {
    console.log('route inside PostData: ', route)
    return fetch(route, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
}
