import * as menu from './menu.js'
import * as utils from './utils.js'
import * as chatbot_ui from './chatbot_ui.js'

document.addEventListener('DOMContentLoaded', (event) => {

    utils.handlePageTransition();
    menu.handleMenuForm();
    chatbot_ui.setupSwipe();
    chatbot_ui.handlePageButtons();

});
