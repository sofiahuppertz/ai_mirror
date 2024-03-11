import * as toolbar from './toolbar.js'

document.addEventListener('DOMContentLoaded', (event) => {
    
    document.getElementById('go-to-page-1').addEventListener('submit', function(event) {
        event.preventDefault(); 
        this.submit();
    });

    toolbar.searchPage();

});