
import * as utils from './utils.js';
import * as chatbot_logic from './chatbot_logic.js';
import * as chatbot_ui from './chatbot_ui.js';

document.addEventListener('DOMContentLoaded', (event) => {

    // Empty chat history: Is this really necessary now that I am ending the chat with a redirection from the server?   
    let chatHistory = document.getElementById('chat-history');
    while (chatHistory.firstChild) {
        chatHistory.removeChild(chatHistory.firstChild);
    }

    // Hide chat and show before-chat buttons: Idem
    document.getElementById('before-chat').style.display = 'block';
    document.getElementById('chat').style.display = 'none';

    // Maybe here is where it shoul start...
    const chatbot_triggers = document.querySelectorAll('#before-chat button');

    chatbot_triggers.forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault();
            chatbot_logic.first_chatbot_message(button);
            chatbot_ui.textFom('/chatbot');
        }, {once: true});
    });
    
});

chatbot_ui.handlePageLink();
