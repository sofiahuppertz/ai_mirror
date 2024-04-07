import * as utils from './utils.js';


// Function to reset the menu display

function resetMenuDisplay() {

    const subelements = document.querySelectorAll('.menu-sub-elem');
    const symbolBtns = document.querySelectorAll('.symbol');
    const contentMenu = document.getElementById('content-menu');
    const menuForm = document.getElementById('menu');
    const closeMenuBtn = document.getElementById('close-menu-btn');
    const menuBtn = document.getElementById('menu-btn');

    subelements.forEach((subelement) => {
        subelement.style.display = 'none';
    });
    symbolBtns.forEach((symbolBtn) => {
        symbolBtn.innerHTML = '+';
    });
    menuBtn.style.display = 'flex';
    contentMenu.style.display = 'none';
    closeMenuBtn.style.display = 'none';
    menuForm.style.right = 'auto';
    menuForm.style.left = '2vw';
}

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
        
        let action = event.target;
        if (action.tagName !== 'BUTTON') {
            action = action.closest('button');
        }

        let value = action.dataset.value;
        if (value === 'open') {
            menuBtn.style.display = 'none';
            closeMenuBtn.style.display = 'block';
            contentMenu.style.display = 'block';
            clonedMenuForm.style.left = 'auto';
            clonedMenuForm.style.right = '2vw';
            handleMenuContent();
        }
        else if (value === 'close') {
            resetMenuDisplay();
        }

    });
}

// Function to handle the menu content

export function handleMenuContent() {
    const menuContent = document.getElementById('content-menu');
    const clonedMenuContent = menuContent.cloneNode(true);
    
    menuContent.parentNode.replaceChild(clonedMenuContent, menuContent);
    const sections = [7, 15, 28, 44, 51, 67, 83, 92, 104, 116, 127, 137];

    clonedMenuContent.addEventListener('click', function(event) {
        event.preventDefault();

        const menuBtn = document.getElementById('menu-btn');
        let target = event.target;


        // If the target is not a button, find the closest parent button
        if (target.tagName !== 'BUTTON') {
            target = target.closest('button');
        }
        
        const value = target.dataset.value;
        const numValue = Number(value);
        
        if(value == 'elem-0') {
            resetMenuDisplay();
            utils.handlePageChange('previous', 0);
        }
        else if (value == 'elem-5') {
            resetMenuDisplay();
            utils.handlePageChange('previous', -1);
        }
        else if (value == 'elem-6') {
            resetMenuDisplay();
            utils.handlePageChange('previous', -2);
        }
        else  if (value == 'elem-1') {
            resetMenuDisplay();
            utils.handlePageChange('next', 0);
        }
        else if (!isNaN(numValue) && numValue >= 0 && numValue <= 11) {
            resetMenuDisplay();
            utils.handlePageChange('next', sections[numValue] - 1);
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