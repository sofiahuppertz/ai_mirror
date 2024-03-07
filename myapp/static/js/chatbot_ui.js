

import * as utils from './utils.js';


// FUNCTION FOR HANDLING SERVER RESPONSE AND REDIRECT TO NEXT FORM

function handleServerRespone (data) {

    // Remove typing indicator
    let typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.parentNode.removeChild(typingIndicator);
    }

    // Append server response to chat history
    utils.send_message(data.server_response, 'chatbot_response');

    // Check if chatbot should end conversation
    if (data.reset_page === "True") {
        return endConversation();
    }
    // Setup next form (Input field or Yes/No buttons)
    if (data.buttons === "True") {
        return binaryForm(data.route);
    }
    else {
        return textFom(data.route);
    }
}

// FUNCTIONS FOR HANDLING TEXT FORM

function handleTextInput(event, route) {

    event.preventDefault();

    document.getElementById('before-chat').style.display = 'none';

    // Check if user input is empty
    if (!utils.isInputNotEmpty()){
        return;
    }

    // Append user input to chat history
    let userInput = document.querySelector('#userInput').value;
    utils.send_message(userInput, 'user_message');

    // Clear user input field
    document.querySelector('#userInput').value = '';

    // Send user input to server and handle server response
    utils.createTypingIndicator();

    //Send data to server
    utils.postData(route, {user_input: userInput})
    .then(response => response.json())
    .then(data => handleServerRespone(data))
}
 


export function textFom(route, start_chat=false) {

    // Change the class of chat-inputs
    const chatInputs = document.getElementById('chat-inputs');
    chatInputs.className = '';
    chatInputs.className = 'chat-inputs-text';

    //Enable reset button
    resetButtonForm();

    // Hide Yes/No buttons and show input field
    const binary_form = document.getElementById('yes-no-form');
    const user_input = document.getElementById('user-input');

    binary_form.style.display = 'none';
    user_input.style.display = 'flex';

    // Store information in localStorage
    if (!start_chat){
        localStorage.setItem('currentFunction', 'textForm');
        localStorage.setItem('nextRoute', route);
    }


    // Add event listener to input field and enter key
    const inputBtn = document.querySelector('#user-input button');


    const clonedInputBtn = inputBtn.cloneNode(true);
    inputBtn.parentNode.replaceChild(clonedInputBtn, inputBtn);


    // Add a new 'click' event listener
    clonedInputBtn.addEventListener('click', function(event) {
        handleTextInput(event, route);
    } );

    const userInputElem = document.getElementById('userInput');
    
    // Remove any existing 'keydown' event listeners

    const clonedUserInputElem = userInputElem.cloneNode(true);
    userInputElem.parentNode.replaceChild(clonedUserInputElem, userInputElem);
    
    // Add a new 'keydown' event listener
    clonedUserInputElem.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            handleTextInput(event, route);
        }
    });
}

// FUNCTION FOR HANDLING YES/NO BUTTONS

function handleBinaryFormEvent (event, route) {

    event.preventDefault();

    let buttonValue = event.submitter.value;

    // Add message to chat
    utils.send_message(buttonValue, 'user_message');
    
    utils.createTypingIndicator();

    // Send button value to server and handle server response
    utils.postData(route, { user_input: buttonValue })
    .then(response => response.json())
    .then(data => handleServerRespone(data));
    return ;
}

export function binaryForm(route) {

    //Hide before chat buttons
    document.getElementById('before-chat').style.display = 'none';

    // Change the class of chat-inputs
    const chatInputs = document.getElementById('chat-inputs');
    chatInputs.className = '';
    chatInputs.className = 'chat-inputs-binary';

    // Hide input field and show Yes/No buttons
    const binary_form = document.getElementById('yes-no-form');
    const user_input = document.getElementById('user-input');

    binary_form.style.display = 'flex';
    user_input.style.display = 'none';

    // Add to localStorage the info:
    localStorage.setItem('currentFunction', 'binaryForm');
    localStorage.setItem('nextRoute', route);

    const clonedBinaryForm = binary_form.cloneNode(true);
    binary_form.parentNode.replaceChild(clonedBinaryForm, binary_form);

    // Add event listener to Yes/No buttons
    clonedBinaryForm.addEventListener('submit', function(event) {
        handleBinaryFormEvent(event, route);
    }, {once: true});
        
    //Enable reset button
    resetButtonForm();
}

// FUNCTION TO RESUME CHAT

export function resume_chat(currentFunction, nextRoute) {
    
    // Hide before-chat buttons
    document.getElementById('before-chat').style.display = 'none';
    // Show chat inputs
    document.getElementById('chat-inputs').style.display = 'flex';

    // Clear local storage
    localStorage.removeItem('currentFunction');
    localStorage.removeItem('nextRoute');
    
    // Call the function that was interrupted
    if (currentFunction == 'textForm') {
        return textFom(nextRoute);
    }
    else if (currentFunction == 'binaryForm') {
        return binaryForm(nextRoute);
    }
    else if (currentFunction == 'endConversation') {
        return endConversation();
    }
}

// FUNCTION TO START THE CHAT

export function start_chat(){ 
    
    // Show before-chat buttons
    document.getElementById('before-chat').style.display = 'flex';
    

    textFom('/chatbot', true);

    // Maybe here is where it shoul start...
    let chatbot_triggers = document.querySelectorAll('#before-chat button');

    // Clone the buttons without their event listeners and replace the original buttons with the clones
    chatbot_triggers.forEach(button => {
        let clone = button.cloneNode(true);
        button.parentNode.replaceChild(clone, button);
    });

    // Update chatbot_triggers to get the cloned buttons
    chatbot_triggers = document.querySelectorAll('#before-chat button');

    chatbot_triggers.forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault();
            first_chatbot_message(button);
            textFom('/chatbot');
        }, {once: true});
    });
    return;
}

export function first_chatbot_message(button) {

    let chatbotMessage;

    document.getElementById('before-chat').style.display = 'none';
    
    if (button.value == 'client_answer') {
        chatbotMessage = "...Thanks for your help. Answers are limited to 270 characters.";
    }
    else if (button.value == 'client_question') {
        chatbotMessage = "Please add your question on the future of A.I.";
    }
    utils.send_message(chatbotMessage, 'chatbot_response');
}


// FUNCTIONS FOR ENDING THE CHAT 

export function clearConversation() {

    // Clear the chat history in the DOM
    let chatHistory = document.querySelector('#chat-history');
    while (chatHistory.firstChild) {
        chatHistory.removeChild(chatHistory.firstChild);
    }
    // Send a POST request to the server to clear the chat history server-side
    utils.postData('/reset_chat', {})
        .then(response => response.json())
        .then(data => { 
            localStorage.removeItem('currentFunction');
            localStorage.removeItem('nextRoute');
            start_chat();
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

export function resetButtonForm() {

    const resetChat = document.getElementById('reset-chat');

    // Remove any existing 'click' event listeners
    const clonedResetChat = resetChat.cloneNode(true);
    resetChat.parentNode.replaceChild(clonedResetChat, resetChat);

    clonedResetChat.addEventListener('click', function(event) {
        clearConversation();
    }, {once: true});
}


export function endConversation() {

    localStorage.setItem('currentFunction', 'endConversation');
    localStorage.setItem('nextRoute', ' ')

    //Enable reset button
    resetButtonForm();

    // Hide Yes/No buttons and input field, only show the reset button
    const binary_form = document.getElementById('yes-no-form');
    const user_input = document.getElementById('user-input');
    const resetChat = document.getElementById('reset-chat');
    
    binary_form.style.display = 'none';
    user_input.style.display = 'none';
    resetChat.style.display = 'flex';
}

// FUNCTION FOR HANDLING PAGE LINKS

export function handlePageLink () {
    document.querySelector('#chatbot-container').addEventListener('click', function(event) {
        if (event.target.matches('#page-link')) {

            event.preventDefault();
    
            var pageNumber = event.target.getAttribute('data-page-number');
            utils.postData('/page/' + pageNumber, {index: pageNumber}, false)
            .then(response => {
                if (response.ok) {
                    window.location.href = '/';
                }
            });
        }
    });
}

