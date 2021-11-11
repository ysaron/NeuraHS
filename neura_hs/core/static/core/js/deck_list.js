'use strict';

document.addEventListener("DOMContentLoaded", function() {
    addAccordionListeners();
    addCopyDeckstringListeners();
})

function addAccordionListeners() {
    let accs = document.getElementsByClassName("deck-accordion");
    console.log(accs);
    for (let i = 0; i < accs.length; i++) {
        accs[i].addEventListener("click", showCards);
    }
}

function showCards() {
    this.classList.toggle("deck-accordion-active");
    let cards = this.parentNode.parentNode.parentNode.parentNode.nextElementSibling;
    console.log(this);
    console.log(cards);
    (cards.style.maxHeight) ?
        cards.style.maxHeight = null :
        cards.style.maxHeight = cards.scrollHeight + "px";
}

function addCopyDeckstringListeners() {
    let copyButtons = document.getElementsByClassName("copy-deck");
    for (let i = 0; i < copyButtons.length; i++) {
        copyButtons[i].addEventListener("click", copyDeckstring);
        copyButtons[i].addEventListener("mouseover", showCopyTooltip);
    }
}

function copyDeckstring() {
    let deckString = this.parentNode.nextElementSibling;
    let input = document.createElement("textarea");
    input.value = deckString.textContent;
    document.body.appendChild(input);
    input.select();
    input.setSelectionRange(0, 99999);
    navigator.clipboard.writeText(input.value);
    input.remove();
    let tooltip = this.firstElementChild;
    tooltip.innerHTML = "Copied!";
}

function showCopyTooltip() {
    let tooltip = this.firstElementChild;
    tooltip.innerHTML = "Copy to clipboard";
}
