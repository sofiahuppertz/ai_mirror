import * as utils from './utils.js';
import * as chatbot_ui from './chatbot_ui.js';

document.addEventListener('DOMContentLoaded', (event) => {

    // Add to the html all the divs of the chatbot
    utils.add_previous_chat();

    // Add event listener totrigger the chatbot
    const chatbot_button = document.getElementById('chatbot-button');
    const chatbot_container = document.getElementById('chatbot-container');
    const close_button = document.getElementById('close-chatbot-button');

    // Display chatbot 
    chatbot_button.addEventListener('click', (event) => {
        
        event.preventDefault();
        chatbot_container.style.display = 'flex';
        chatbot_button.style.display = 'none';

        // Close chatbot when close button is clicked
        close_button.addEventListener('click', (event) => {
            event.preventDefault();
            chatbot_container.style.display = 'none';
            chatbot_button.style.display = 'block';
        }, {once: true});

        // Check if there's any saved state in localStorage
        let currentFunction = localStorage.getItem('currentFunction');
        let nextRoute = localStorage.getItem('nextRoute');

        console.log("currentFunction: ", currentFunction);
        console.log("nextRoute: ", nextRoute);
        // Go to saved state in conversation
        if (currentFunction && nextRoute)
        {
            chatbot_ui.resume_chat(currentFunction, nextRoute);
        }
        // Start chat from the beginning
        else
        {
            chatbot_ui.start_chat();
        }
        return;
    });
    
});

chatbot_ui.handlePageLink();
