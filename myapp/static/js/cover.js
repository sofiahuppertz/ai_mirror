import * as menu from './menu.js'
import * as chatbot_ui from './chatbot_ui.js';

document.addEventListener('DOMContentLoaded', (event) => {
    menu.handleMenuForm();
    chatbot_ui.setupSwipe();
    chatbot_ui.handlePageButtons();

});
