import * as utils from './utils.js';
import * as chatbot_ui from './chatbot_ui.js';

document.addEventListener('DOMContentLoaded', (event) => {
    
    document.getElementById('go-to-page-1').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission
        this.submit(); // Submit the form to go to page 1
    });

    chatbot_ui.searchPage();

});