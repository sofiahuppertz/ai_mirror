import * as utils from './utils.js';
import * as chatbot_ui from './chatbot_ui.js';
import * as toolbar from './toolbar.js';



document.addEventListener('DOMContentLoaded', (event) => {

    // Handle page transition
    utils.handlePageTransition();

    // Add to the html all the divs of the chatbot
    utils.add_previous_chat();

    // Add event listener totrigger the chatbot
    const chatbot_button = document.getElementById('chatbot-button');
    const chatbot_container = document.getElementById('chatbot-container');
    const shrink_chatbot_btn = document.getElementById('shrink-chat');

    // Display chatbot 
    chatbot_button.addEventListener('click', (event) => {

        console.log("hello");

        event.preventDefault();
        
        chatbot_container.style.display = 'flex';
        chatbot_button.style.display = 'none';

        // Check if there's any saved state in localStorage
        let currentFunction = localStorage.getItem('currentFunction');
        let nextRoute = localStorage.getItem('nextRoute');

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

    function shrink_chatbot(event)
    {
        event.preventDefault();
        chatbot_container.style.display = 'none';
        chatbot_button.style.display = 'block';
    }

    // Close chatbot when close button is clicked
    shrink_chatbot_btn.addEventListener('click', (event) => {
        shrink_chatbot(event);
    
    });

    // Close chatbot when escape key is pressed
    window.addEventListener('keydown', (event) => {
        if (event.key === 'Escape')
        {
            shrink_chatbot(event);
        }
    });

    chatbot_ui.handlePageLink();
    toolbar.handleMenuForm();
    chatbot_ui.setupSwipe();

});
