document.getElementById("start-debate").addEventListener("click", async function () {
    let debateRule = document.getElementById("debate-rule").value;
    let response = await fetch("/api/debate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rule: debateRule })
    });
    let data = await response.json();
    document.getElementById("agent1-response").innerText = data.agent1;
    document.getElementById("agent2-response").innerText = data.agent2;
    document.getElementById("contradiction-result").innerText = data.contradiction_found ? "Yes" : "No";
});
