
// Function to handle event to change page.
export function change_page(value, pageNumber) {
    
    // Check if we are at the last page of a chapter and the user wants to go to the next page.
    const chapters_last_pages = [0, 6, 14, 27, 43, 50, 66, 82, 91, 103, 115, 126, 136];
    
    if (chapters_last_pages.includes(pageNumber) && value === 'next') {
        // Get the index of the current page in the chapters_last_pages array
        let index = chapters_last_pages.indexOf(pageNumber);
        
        // Define the transition image adress
        let imageAdress = '../static/images/transitions/transition-' + index + '.svg';
        // Show the transition.
        const overlay = document.getElementById('transition-overlay');
        const transitionImage = document.getElementById('transition-img');

        transitionImage.src = imageAdress;
        overlay.style.visibility = 'visible';

        setTimeout(() => {
            overlay.style.visibility = 'hidden';
        }, 3000);
    }

    fetch('/page/' + pageNumber, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'action': value
        })
    })
    .then(response => {
        if (response.ok) {
            window.location.href = '/';
        }
    });
}


// FUNCTION TO HANDLE PAGE TRANSITION
export function handlePageTransition() {
    window.onload = function() {
        document.getElementById('book-container').classList.add('loaded');
    };

    // Get the page buttons
    const pageButtons = document.querySelectorAll('.page-buttons button');

    // Add event listener to each button
    pageButtons.forEach(button => {
        button.addEventListener('click', function() {
            document.getElementById('book-container').classList.remove('loaded');
        });
    });
}


// FUNCTION TO CHECK IF PAGE IS ZOOMED
export function isPageZoomed() {
    var viewportWidth = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
    var windowWidth = window.outerWidth || window.innerWidth;

    var zoomFactor = windowWidth / viewportWidth;

	return zoomFactor !== 1;
}


// FUNCTION TO APPEAR MESSAGES IN CHAT

export function send_message(message, className){
    let chatMessageDiv = document.createElement('div');
    chatMessageDiv.innerHTML = message;
    chatMessageDiv.className = className;
    let chatHistory = document.querySelector('#chat-history');
    chatHistory.appendChild(chatMessageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// FUNCTION TO CREATE TYPING INDICATOR

export function createTypingIndicator() {
    let typingIndicator = document.createElement('div');
    typingIndicator.id = 'typingIndicator';
    typingIndicator.innerHTML = '<span></span><span></span><span></span>';
    let chatHistory = document.querySelector('#chat-history');
    chatHistory.appendChild(typingIndicator);
}

//FUNNTION TO SEND DATA TO SERVER

export function postData(method, route, data, clearStorage=true) {

    if (clearStorage) {
        localStorage.removeItem('currentFunction');
        localStorage.removeItem('nextRoute');
    }

    if (method === 'GET') {
        return fetch(route, {
            method: method
        });
    }
    else {
        return fetch(route, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
    }
}

// FUNCTION TO APPEND PREVIOUS CHATS

export function add_previous_chat(){

    fetch('/get_previous_chat', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        let history = data['response'];
        if (history === null) {
            return;
        }
        for (let i = 0; i < history.length ; i++) {
            let user_message = history[i]['user_message'];
            let chatbot_response = history[i]['chatbot_response'];
            if (user_message)
            {
                send_message(user_message, 'user_message');
            }
            if (chatbot_response)
            {
                send_message(chatbot_response, 'chatbot_response');
            }
        }
    })
}

// FUNCTION TO CHECK INPUT ISN'T EMPTY

export function isInputNotEmpty() {

    const userInput = document.getElementById('userInput');
    if (userInput && userInput.value && userInput.value.trim() !== '') {
        return true;
    }
    
    return false;
}

// FUNCTION TO CHECK INPUT LENGTH IS VALID

export function checkTokenLimit(input, tokenLimit=100) {

    const tokens = input.split(/\s+/);  

    if (tokens.length > tokenLimit) {
        alert("Token limit exceeded. Your message will be truncated.");
        input = tokens.slice(0, tokenLimit).join(" ");
    }
    return input;
}

// FUNCTION TO CHECK PAGE NUMBER IS VALID

export function isValidPageNumber(input) {

    if (input === '' || isNaN(input) || parseInt(input) < 1) {
        alert('Please enter a valid page number greater than 0.');
        return false;
    }
    return true;
}


