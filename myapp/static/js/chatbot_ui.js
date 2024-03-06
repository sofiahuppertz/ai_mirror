

import * as utils from './utils.js';


// FUNCTION FOR HANDLING SERVER RESPONSE AND REDIRECT TO NEXT FORM

function handleServerRespone (data) {
    // Append server response to chat history
    utils.send_message(data.server_response, 'chatbot_response');

    console.log("Route in handleServerResponse: ", data.route)
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


    console.log("Route in handleTextInput: ", route)
    // Check if user input is empty
    let userInput = document.querySelector('#userInput').value;
    if (userInput == '') {
        return;
    }

    // Append user input to chat history
    utils.send_message(userInput, 'user_message');

    // Clear user input field
    document.querySelector('#userInput').value = '';

    // Send user input to server and handle server response
    console.log(userInput);
    utils.postData(route, {user_input: userInput})
    .then(response => response.json())
    .then(data => handleServerRespone(data))
}



export function textFom(route) {
    
    console.log("Route in textForm: ", route)

    //Enable reset button
    resetButtonForm();

    // Hide Yes/No buttons and show input field
    const binary_form = document.getElementById('yes-no-form');
    const user_input = document.getElementById('user-input');

    binary_form.style.display = 'none';
    user_input.style.display = 'flex';

    // Store information in localStorage
    localStorage.setItem('currentFunction', 'textForm');
    localStorage.setItem('nextRoute', route);


    // Add event listener to input field and enter key
    const inputBtn = document.querySelector('#user-input button');
    inputBtn.addEventListener('click', function(event) {
        handleTextInput(event, route);
    } , {once: true});

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

function setupButton(buttonClass, initialClass, clickClass) {
    let button = document.querySelector(buttonClass);
    button.disabled = false;
    button.classList.remove(clickClass);
    button.classList.add(initialClass);
    button.onclick = function() {
        this.classList.remove(initialClass);
        this.classList.add(clickClass);
    };
}

export function binaryForm(route) {

    console.log("Route in binaryForm: ", route)

    // Hide input field and show Yes/No buttons
    const binary_form = document.getElementById('yes-no-form');
    const user_input = document.getElementById('user-input');

    binary_form.style.display = 'flex';
    user_input.style.display = 'none';

    // Add to localStorage the info:
    localStorage.setItem('currentFunction', 'binaryForm');
    localStorage.setItem('nextRoute', route);


    // Setup buttons UI
    setupButton('.yes-button', 'btn-success', 'btn-dark');
    setupButton('.no-button', 'btn-danger', 'btn-dark');

    // Add event listener to Yes/No buttons
    binary_form.addEventListener('submit', (event) => {

        event.preventDefault();

        let buttonValue = event.submitter.value;

        // Append button value to chat history
        utils.send_message(buttonValue, 'user_message');

        // Disable buttons
        document.querySelector('.yes-button').disabled = true;
        document.querySelector('.no-button').disabled = true;
        
        // Send button value to server and handle server response
        utils.postData(route, { user_input: buttonValue })
        .then(response => response.json())
        .then(data => handleServerRespone(data));
    }, {once: true});

    //Enable reset button
    resetButtonForm();
}

// FUNCTION TO RESUME CHAT

export function resume_chat(currentFunction, nextRoute) {
    
    console.log("Inside resume_chat");
    // Hide "conversation starter" buttons and show chat input fields
    document.getElementById('before-chat').style.display = 'none';
    document.getElementById('chat-inputs').style.display = 'flex';

    // Clear local storage
    localStorage.removeItem('currentFunction');
    localStorage.removeItem('nextRoute');
    
    // Call the function that was interrupted
    if (currentFunction == 'textForm') {
        console.log("calling textForm");
        textFom(nextRoute);
    }
    else if (currentFunction == 'binaryForm') {
        console.log("calling binaryForm");
        binaryForm(nextRoute);
    }
    else if (currentFunction == 'endConversation') {
        console.log("calling endConversation");
        endConversation();
    }
}

// FUNCTION TO START THE CHAT

export function start_chat(){ 

    console.log("Inside start_chat");
    // Hide chat and show before-chat buttons: Idem
    document.getElementById('before-chat').style.display = 'flex';
    document.getElementById('chat-inputs').style.display = 'none';

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
    document.getElementById('chat-inputs').style.display = 'flex';
    
    if (button.value == 'client_answer') {
        chatbotMessage = "...Thanks for your help. Answers are limited to 270 characters.";
    }
    else if (button.value == 'client_question') {
        chatbotMessage = "Please add your question on the future of A.I.";
    }
    utils.send_message(chatbotMessage, 'chatbot_response');
}


// FUNCTIONS FOR ENDING THE CHAT 

export function resetButtonForm() {

    const resetChat = document.getElementById('reset-chat');

    resetChat.addEventListener('click', function(event) {
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
            console.log(pageNumber);
            utils.postData('/page/' + pageNumber, {index: pageNumber})
            .then(response => {
                if (response.ok) {
                    window.location.href = '/';
                }
            });
        }
    });
}

