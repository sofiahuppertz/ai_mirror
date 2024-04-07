import { handleMenuForm} from './menu.js'
import { handlePageTransition } from './utils.js';
import { setupSwipe, handlePageButtons } from './chatbot_ui.js';

document.addEventListener('DOMContentLoaded', (event) => {

    handlePageTransition();
    handleMenuForm();
    setupSwipe();
    handlePageButtons();

});
