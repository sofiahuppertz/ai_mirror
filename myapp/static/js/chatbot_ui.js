
import * as chatbot_logic from './chatbot_logic.js';
import * as utils from './utils.js';

// FUNCTION FOR HANDLING RESET BUTTON

export function resetButtonForm() {

    const binary_form = document.getElementById('yes-no-form');
    const user_input = document.getElementById('user-input');
    const resetChat = document.getElementById('reset-chat');
    
    binary_form.style.display = 'none';
    user_input.style.display = 'none';
    resetChat.style.display = 'flex';

    resetChat.addEventListener('submit', (event) => {
        event.preventDefault(); // Prevent form submission
        utils.postData('/', {})
        .then(response => {
            if (response.ok) {
                window.location.href = '/';
            }
        });
    });
}

// FUNCTION FOR HANDLING SERVER RESPONSE (COMMON TO BOTH FORMS)

function handleServerRespone (data) {
    // Append server response to chat history
    utils.send_message(data.server_response, 'chatbot-message');

    console.log("Route in handleServerResponse: ", data.route)
    // Check if chatbot should end conversation
    if (data.reset_page === "True") {
        //return resetButtonForm();
        return resetButtonForm();
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
    utils.send_message(userInput, 'user-message');

    // Clear user input field
    document.querySelector('#userInput').value = '';

    // Send user input to server and handle server response
    utils.postData(route, {user_input: userInput})
    .then(response => response.json())
    .then(data => handleServerRespone(data))
}



export function textFom(route) {
    console.log("Route in textForm: ", route)
    // Hide Yes/No buttons and show input field
    const binary_form = document.getElementById('yes-no-form');
    const user_input = document.getElementById('user-input');

    binary_form.style.display = 'none';
    user_input.style.display = 'flex';

    // Add event listener to input field and enter key
    const inputBtn = document.querySelector('#input-container button');
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

    // Setup buttons UI
    setupButton('.yes-button', 'btn-success', 'btn-dark');
    setupButton('.no-button', 'btn-danger', 'btn-dark');

    // Add event listener to Yes/No buttons
    binary_form.addEventListener('submit', (event) => {

        event.preventDefault();

        let buttonValue = event.submitter.value;

        // Append button value to chat history
        utils.send_message(buttonValue, 'user-message');

        // Disable buttons
        document.querySelector('.yes-button').disabled = true;
        document.querySelector('.no-button').disabled = true;
        
        // Send button value to server and handle server response
        utils.postData(route, { button_value: buttonValue })
        .then(response => response.json())
        .then(data => handleServerRespone(data));
    }, {once: true});
}

// FUNCTION FOR HANDLING PAGE LINKS

export function handlePageLink () {
    document.querySelector('#chat').addEventListener('click', function(event) {
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

