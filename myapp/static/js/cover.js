import * as toolbar from './toolbar.js'
import * as utils from './utils.js'
import { setupSwipe } from './chatbot_ui.js';

document.addEventListener('DOMContentLoaded', (event) => {
    toolbar.handleMenuForm();
    setupSwipe();

});
