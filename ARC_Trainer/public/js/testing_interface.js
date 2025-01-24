document.getElementById("submit-challenge").addEventListener("click", function() {
    let challengeInput = document.getElementById("challenge-input").value;

    fetch('/api/submit-challenge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input: challengeInput })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("ai-response").innerText = "AI's Response: " + data.message;
    })
    .catch(error => console.error("Error:", error));
});