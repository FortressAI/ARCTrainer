function setMode(mode) {
    localStorage.setItem("selectedMode", mode);
    window.location.href = mode === "arc" ? "/arc-mode" : mode === "last-human" ? "/last-human" : "/debate-mode";
}
