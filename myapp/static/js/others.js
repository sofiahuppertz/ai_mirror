import { handleMenuForm } from './menu.js'
import { handlePageTransition } from './utils.js'

document.addEventListener('DOMContentLoaded', (event) => {
    handlePageTransition();
    handleMenuForm();
});
