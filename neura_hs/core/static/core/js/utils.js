function showDeckSaveForm() {
  var dnf = document.getElementById("deckSaveForm");
  var btn = document.getElementById("deckSaveButton");
  if (dnf.style.display === "none") {
    dnf.style.display = "block";
    btn.style.display = "none";
  }
}