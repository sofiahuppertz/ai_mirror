import { handleMenuForm} from './menu.js'
import { setupSwipe, handlePageButtons } from './chatbot_ui.js';

document.addEventListener('DOMContentLoaded', (event) => {
    handleMenuForm();
    setupSwipe();
    handlePageButtons();

});
