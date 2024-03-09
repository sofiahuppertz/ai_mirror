import * as utils from './utils.js';

// Function to search for a page

export function showSearchPage() {
    const showSearch = document.getElementById('show-search-bar');
    const searchPageForm = document.getElementById('search-page');


    const clonedShowSearch = showSearch.cloneNode(true);
    showSearch.parentNode.replaceChild(clonedShowSearch, showSearch);

    clonedShowSearch.addEventListener('click', function(event) {
        event.preventDefault();
        
        clonedShowSearch.style.display = 'none';
        searchPageForm.style.display = 'flex';
        
        const searchInput = document.getElementById('search-input');
        
        let width = 0;
        const expandWidth = setInterval(() => {
            width += 3;
            searchInput.style.width = `${width}px`; // Set the new width
    
            if (width >= 100) {
                searchInput.focus();
                clearInterval(expandWidth);
            }
        }, 1); 

        searchPage();
        closeSearch();
    });
}

function closeSearchEvent(event) {
    
    event.preventDefault();

    const searchPageForm = document.getElementById('search-page');
    const showSearch = document.getElementById('show-search-bar');

    searchPageForm.removeEventListener('keydown', keyDownSearchForm);

    const searchInput = document.getElementById('search-input');

    searchInput.value = '';

    let width = 100;
    const reduceWidth = setInterval(() => {
        width -= 3;
        searchInput.style.width = `${width}px`; // Set the new width

        if (width <= 0) {
            clearInterval(reduceWidth);
            searchPageForm.style.display = 'none';
            showSearch.style.display = 'flex'
            showSearchPage();
        }
    }, 3);
}


export function closeSearch() {

    const closeSearch = document.getElementById('close-search');

    const clonedCloseSearch = closeSearch.cloneNode(true);
    closeSearch.parentNode.replaceChild(clonedCloseSearch, closeSearch);

    clonedCloseSearch.addEventListener('click', function(event) {
        closeSearchEvent(event);
    });
}

function handleSearchPage(event) {

    event.preventDefault();
    const searchPageForm = document.getElementById('search-page');

    var input = document.getElementById('search-input').value.trim();        
    // Empty input field
    document.getElementById('search-input').value = '';
    // Check if input is valid
    if (!utils.isValidPageNumber(input))
    {
        return;
    }
    searchPageForm.setAttribute('action', '/page/' + input);
    searchPageForm.submit();
}

function keyDownSearchForm(event){

    
    if (event.key === 'Enter') {
        handleSearchPage(event);
    }
    if (event.key === 'Escape') {
        event.preventDefault();
        closeSearchEvent(event);
    }
}

// Function to search for a page
export function searchPage() {
    
    const searchButton = document.getElementById('search-button');
    const clonedSearchButton = searchButton.cloneNode(true);
    const searchPageForm = document.getElementById('search-page');
    //const clonedPageForm = searchPageForm.cloneNode(true);


    searchButton.parentNode.replaceChild(clonedSearchButton, searchButton);

    clonedSearchButton.addEventListener('click', function(event) {
        handleSearchPage(event);
    });

    //searchPageForm.parentNode.replaceChild(clonedPageForm, searchPageForm);
    searchPageForm.addEventListener('keydown', keyDownSearchForm);
}