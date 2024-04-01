import * as toolbar from './toolbar.js'
import * as utils from './utils.js'

document.addEventListener('DOMContentLoaded', (event) => {

    utils.handlePageTransition();
    toolbar.showSearchPage();
    //chatbot_ui.setupSwipe();
    //chatbot_ui.handlePageButtons();
});
