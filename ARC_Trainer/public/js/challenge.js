document.getElementById("submit-challenge").addEventListener("click", function () {
    let challengeInput = document.getElementById("challenge-input").value;

    fetch('/api/start-challenge', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: challengeInput }),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("ai-response").innerText = "AI's Response: " + data.message;
    })
    .catch(error => console.error("Error:", error));
});

document.getElementById("start-debate").addEventListener("click", function () {
    let debateRule = document.getElementById("debate-rule").value;

    fetch('/api/debate', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rule: debateRule }),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("agent1-response").innerText = data.agent1;
        document.getElementById("agent2-response").innerText = data.agent2;
        document.getElementById("contradiction-result").innerText = data.contradiction_found ? "Yes" : "No";
    })
    .catch(error => console.error("Error:", error));
});
