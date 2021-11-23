function showDeckSaveForm() {
  var form = document.getElementById("deckSaveForm");
  var ctrl_buttons = document.getElementById("deckControlButtons2");
  form.style.display = "flex";
  ctrl_buttons.style.display = "none";
}

function showDeckRenameForm() {
  var form = document.getElementById("deckRenameForm");
  var ctrl_buttons = document.getElementById("deckControlButtons");
  form.style.display = "flex";
  ctrl_buttons.style.display = "none";
}

function showDeckDeleteForm() {
  var form = document.getElementById("deckDeleteForm");
  var ctrl_buttons = document.getElementById("deckControlButtons");
  form.style.display = "flex";
  ctrl_buttons.style.display = "none";
}

function hideDeckSaveForm() {
  var form = document.getElementById("deckSaveForm");
  var ctrl_buttons = document.getElementById("deckControlButtons2");
  form.style.display = "none";
  ctrl_buttons.style.display = "flex";
}

function hideDeckDeleteForm() {
  var form = document.getElementById("deckDeleteForm");
  var ctrl_buttons = document.getElementById("deckControlButtons");
  form.style.display = "none";
  ctrl_buttons.style.display = "flex";
}

function hideDeckRenameForm() {
  var form = document.getElementById("deckRenameForm");
  var ctrl_buttons = document.getElementById("deckControlButtons");
  form.style.display = "none";
  ctrl_buttons.style.display = "flex";
}

function copyToClipboard() {
  let copyDeckBlock = document.getElementById("deckstringToCopy");
  let copyText = copyDeckBlock.firstElementChild;
  if (navigator.clipboard) {    // Если Clipboard API доступно (localhost / HTTPS)
      copyText.select();
      copyText.setSelectionRange(0, 99999);     /* Для мобильных устройств */
      navigator.clipboard.writeText(copyText.value);
      let tooltip = document.getElementById("copyTooltip");
      tooltip.innerHTML = "Copied!";
  } else {
      let ctrl_buttons = document.getElementById("deckControlButtons");
      if (ctrl_buttons == undefined) ctrl_buttons = document.getElementById("deckControlButtons2");
      ctrl_buttons.style.display = "none";
      copyDeckBlock.style.display = "flex";
      copyText.select();
      copyText.setSelectionRange(0, 99999);
      copyText.nextElementSibling.addEventListener("click", function() {
          ctrl_buttons.style.display = "flex";
          copyDeckBlock.style.display = "none";
      });
  }
}

function tooltipFunc() {
  var tooltip = document.getElementById("copyTooltip");
  if (navigator.clipboard) {
        tooltip.innerHTML = "Copy deck code";
    } else {
        tooltip.innerHTML = "Show deck code";
    }
}

function clearDeckstringField() {
    $('#form-deckstring').val('');
}

function mail() {
    let btn = $('#contactBtn');
    let endpoint = btn.attr("data-url");
    $.ajax({
        data: {email: true},
        url: endpoint,
        success: function(response) {btn.empty().text(response.email);},
        error: function(response) {console.log(response.responseJSON.errors);}
    });
}
