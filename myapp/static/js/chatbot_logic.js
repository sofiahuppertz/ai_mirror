
import * as utils from './utils.js';

//FUNCTIONS FOR STARTING THE CHAT

export function first_chatbot_message(button) {

    let chatbotMessage;

    document.getElementById('before-chat').style.display = 'none';
    document.getElementById('chat-inputs').style.display = 'flex';
    
    if (button.value == 'client_answer') {
        chatbotMessage = "...Thanks for your help. Answers are limited to 270 characters.";
    }
    else if (button.value == 'client_question') {
        chatbotMessage = "Please add your question on the future of A.I.";
    }
    utils.send_message(chatbotMessage, 'chatbot_response');
}
