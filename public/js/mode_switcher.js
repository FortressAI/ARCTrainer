function setMode(mode) {
    localStorage.setItem("selectedMode", mode);
    window.location.href = mode === "arc" ? "home.html" : "challenge.html";
}

// Load mode on challenge pages
document.addEventListener("DOMContentLoaded", function () {
    const mode = localStorage.getItem("selectedMode");
    if (mode === "arc") {
        document.getElementById("mode-label").innerText = "ARC Dataset Mode";
        loadArcChallenge();
    } else {
        document.getElementById("mode-label").innerText = "Humanity’s Last Exam Mode";
    }
});
