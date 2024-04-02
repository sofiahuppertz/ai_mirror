import * as utils from './utils.js';

// Function to search for a page

export function handleMenuForm() {

    const menuForm = document.getElementById('menu');


    const clonedMenuForm = menuForm.cloneNode(true);
    menuForm.parentNode.replaceChild(clonedMenuForm, menuForm);

    clonedMenuForm.addEventListener('click', function(event) {
        
        event.preventDefault();

        const menuBtn = clonedMenuForm.querySelector('#menu-btn');
        const closeMenuBtn = clonedMenuForm.querySelector('#close-menu-btn');
        const contentMenu = document.getElementById('content-menu');
        const subelements = document.querySelectorAll('.menu-sub-elem');
        const symbolBtns = document.querySelectorAll('.symbol');
        
        let action = event.target;
        if (action.tagName !== 'BUTTON') {
            action = action.closest('button');
        }

        let value = action.dataset.value;
        console.log(value);
        if (value === 'open') {
            menuBtn.style.display = 'none';
            closeMenuBtn.style.display = 'block';
            contentMenu.style.display = 'block';

            handleMenuContent();
        }
        else if (value === 'close') {
            subelements.forEach((subelement) => {
                subelement.style.display = 'none';
            });
            symbolBtns.forEach((symbolBtn) => {
                symbolBtn.innerHTML = '+';
            });
            menuBtn.style.display = 'flex';
            contentMenu.style.display = 'none';
            closeMenuBtn.style.display = 'none';

        }

    });
}

export function handleMenuContent() {
    const menuContent = document.getElementById('content-menu');
    const clonedMenuContent = menuContent.cloneNode(true);
    menuContent.parentNode.replaceChild(clonedMenuContent, menuContent);

    clonedMenuContent.addEventListener('click', function(event) {
        event.preventDefault();

        let target = event.target;


        // If the target is not a button, find the closest parent button
        if (target.tagName !== 'BUTTON') {
            target = target.closest('button');
        }
        
        const value = target.dataset.value;

        if (value == 'elem-1') {
            utils.change_page('next', 0);
        }
        else {

            let subelements = clonedMenuContent.querySelectorAll(`.${value}`);

            subelements.forEach((subelement) => {
                subelement.style.display = (subelement.style.display == 'flex') ? 'none' : 'flex';            
            });

            let symbolBtns = clonedMenuContent.querySelectorAll('.symbol');

            symbolBtns.forEach((symbolBtn) => {
                if (symbolBtn.dataset.value == value) {
                    symbolBtn.innerHTML = (symbolBtn.innerHTML == '+') ? '-' : '+';
                }
            });

        }
        

    });
}