document.getElementById("start-arc-test").addEventListener("click", function() {
    fetch('/api/arc-test', { method: 'POST' })
    .then(response => response.json())
    .then(data => {
        document.getElementById("arc-response").innerText = "AI's Response: " + data.message;
    })
    .catch(error => console.error("Error:", error));
});
