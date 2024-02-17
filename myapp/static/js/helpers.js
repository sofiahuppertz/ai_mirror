// helpers.js



function first_chatbot_message(button) {
    document.getElementById('before-chat').style.display = 'none';
    document.getElementById('chat').style.display = 'block';
    
    if (button.value == 'client_answer') {
        chatbotMessage = "...Thanks for your help. Answers are limited to 270 characters.";
    }
    else if (button.value == 'client_question') {
        chatbotMessage = "Please add your question on the future of A.I.";
    } 
    send_message(chatbotMessage, 'chatbot-message');
}


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

function end_chat() {
    last_chatbot_message().then(() => {
        postData('/end_chat', {end_chat: 'True'})
        .then(response => response.json())
        .then(data => {
            if (data.redirect){
                window.location.href = data.redirect;
            }
        });
    });
}
    
//OR just set_chatbot....
function reset_chatbot() {
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
            first_chatbot_message(button);
            textFom('/chatbot');
            console.log('route changed to /chatbot');
        }, {once: true});
    });
}


function handleTextInput(event, route) {

    event.preventDefault();

    console.log("HEY!!")
    // Check if user input is empty
    let userInput = document.querySelector('#userInput').value;
    if (userInput == '') {
        return;
    }

    // Append user input to chat history
    send_message(userInput, 'user-message');

    // Clear user input field
    document.querySelector('#userInput').value = '';

    // Send user input to server
    postData(route, {user_input: userInput})
    .then(response => response.json())
    .then(data => {

        // Append server response to chat history
        send_message(data.server_response, 'chatbot-message');

        // Check if chatbot should end conversation
        if (data.end_chat === "True") {
            end_chat();
        }
        // Setup next form (Input field or Yes/No buttons)
        if (data.buttons === "True") {
            return binaryForm('/handle_question');
        }
        else {
            return textFom('/handle_question');
        }
    })
}


function textFom (route) {
    
    // Hide Yes/No buttons and show input field
    const binary_form = document.getElementById('yes-no-form');
    const user_input = document.getElementById('user-input');

    binary_form.style.display = 'none';
    user_input.style.display = 'flex';

    // Add event listener to input field and enter key
    const inputBtn = document.querySelector('#input-container button');
    inputBtn.addEventListener('click', event => handleTextInput(event, route), {once: true});

    document.getElementById('userInput').addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            handleTextInput(event, route);
        }
    }); //Make sure there aren't bugs with this event listener being added multiple times
}


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


function binaryForm(route) {
    const binary_form = document.getElementById('yes-no-form');
    const user_input = document.getElementById('user-input');

    binary_form.style.display = 'flex';
    user_input.style.display = 'none';

    setupButton('.yes-button', 'btn-success', 'btn-dark');
    setupButton('.no-button', 'btn-danger', 'btn-dark');

    binary_form.addEventListener('submit', (event) => {
        event.preventDefault();

        let buttonValue = event.submitter.value;
        send_message(buttonValue, 'user-message');

        document.querySelector('.yes-button').disabled = true;
        document.querySelector('.no-button').disabled = true;

        console.log('Form submitted with button value; ', buttonValue);
        
        postData(route, { button_value: buttonValue })
        .then(response => response.json())
        .then(data => {
            send_message(data.server_response, 'chatbot-message');
            if (data.end_chat === "True") {
                end_chat();
            }
            else if (data.buttons === "True") {
                return binaryForm('/handle_question');
            }
            else {
                return textFom('/handle_question');
            }
        })
    }, {once: true});
}
