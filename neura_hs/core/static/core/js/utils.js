function showDeckSaveForm() {
  var form = document.getElementById("deckSaveForm");
  var ctrl_buttons = document.getElementById("deckControlButtons2");
  if (form.style.display === "none") {
    form.style.display = "block";
    ctrl_buttons.style.display = "none";
  }
}

function showDeckRenameForm() {
  var form = document.getElementById("deckRenameForm");
  var ctrl_buttons = document.getElementById("deckControlButtons");
  if (form.style.display === "none") {
    form.style.display = "block";
    ctrl_buttons.style.display = "none";
  }
}

function showDeckDeleteForm() {
  var form = document.getElementById("deckDeleteForm");
  var ctrl_buttons = document.getElementById("deckControlButtons");
  if (form.style.display === "none") {
    form.style.display = "block";
    ctrl_buttons.style.display = "none";
  }
}

function hideDeckSaveForm() {
  var form = document.getElementById("deckSaveForm");
  var ctrl_buttons = document.getElementById("deckControlButtons2");
  if (form.style.display === "block") {
    form.style.display = "none";
    ctrl_buttons.style.display = "block";
  }
}

function hideDeckDeleteForm() {
  var form = document.getElementById("deckDeleteForm");
  var ctrl_buttons = document.getElementById("deckControlButtons");
  if (form.style.display === "block") {
    form.style.display = "none";
    ctrl_buttons.style.display = "block";
  }
}

function hideDeckRenameForm() {
  var form = document.getElementById("deckRenameForm");
  var ctrl_buttons = document.getElementById("deckControlButtons");
  if (form.style.display === "block") {
    form.style.display = "none";
    ctrl_buttons.style.display = "block";
  }
}