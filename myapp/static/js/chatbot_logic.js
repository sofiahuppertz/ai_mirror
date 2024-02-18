
import * as utils from './utils.js';

//FUNCTIONS FOR STARTING THE CHAT

export function first_chatbot_message(button) {

    let chatbotMessage;

    document.getElementById('before-chat').style.display = 'none';
    document.getElementById('chat').style.display = 'block';
    
    if (button.value == 'client_answer') {
        chatbotMessage = "...Thanks for your help. Answers are limited to 270 characters.";
    }
    else if (button.value == 'client_question') {
        chatbotMessage = "Please add your question on the future of A.I.";
    }
    utils.send_message(chatbotMessage, 'chatbot-message');
}


// FUNCTIONS FOR ENDING THE CHAT 

function last_chatbot_message() {
    return new Promise((resolve, reject) => {
    let countdown = 3;
    let countdownMessageDiv = document.createElement('div');
    countdownMessageDiv.innerHTML = `Restarting chat in ${countdown}`;
    countdownMessageDiv.className = 'chatbot-message';

    let chatHistory = document.querySelector('#chat-history');
    chatHistory.appendChild(countdownMessageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;

    let countdownInterval = setInterval(() => {
        countdown--;
        if (countdown > 0) {
            countdownMessageDiv.innerHTML = `Restarting chat in ${countdown}`;
            chatHistory.scrollTop = chatHistory.scrollHeight;
        } else {
            clearInterval(countdownInterval);
            countdownMessageDiv.innerHTML = 'Goodbye! Enjoy your reading :)';
            chatHistory.scrollTop = chatHistory.scrollHeight;
            resolve();
        }
    }, 1000);
    });
}

export function reset_page() {
    last_chatbot_message().then(() => {
        utils.postData('/reset_page', {reset_page: 'True'})
        .then(response => response.json())
        .then(data => {
            if (data.redirect){
                window.location.href = data.redirect;
            }
        });
    });
}
    



