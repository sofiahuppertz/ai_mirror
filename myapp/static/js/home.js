import * as toolbar from './toolbar.js'

document.addEventListener('DOMContentLoaded', (event) => {
    
    document.getElementById('go-to-page-1').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission
        this.submit(); // Submit the form to go to page 1
    });

    toolbar.searchPage();

});