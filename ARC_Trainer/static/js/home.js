document.getElementById("load-arc-task").addEventListener("click", async function () {
    let taskName = document.getElementById("arc-task").value || "default_task";
    let response = await fetch(`/api/load-arc-task?task_name=${taskName}`);
    let data = await response.json();
    document.getElementById("arc-task-output").innerText = JSON.stringify(data, null, 2);
});

document.getElementById("submit-challenge").addEventListener("click", async function () {
    let challengeInput = document.getElementById("challenge-input").value;
    let response = await fetch("/api/start-challenge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: challengeInput })
    });
    let data = await response.json();
    document.getElementById("challenge-response").innerText = data.message;
});
