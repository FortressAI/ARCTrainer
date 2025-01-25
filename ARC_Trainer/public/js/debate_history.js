async function fetchDebateHistory(rule) {
    try {
        const response = await fetch(`/api/get-debate-history?rule=${encodeURIComponent(rule)}`);
        const debates = await response.json();

        const historyContainer = document.getElementById("debate-history");
        historyContainer.innerHTML = ""; // Clear existing content

        if (debates.length === 0) {
            historyContainer.innerHTML = "<p>No past debates found for this rule.</p>";
            return;
        }

        debates.forEach(debate => {
            let debateEntry = document.createElement("div");
            debateEntry.classList.add("debate-entry");

            debateEntry.innerHTML = `
                <p><strong>Agent 1:</strong> ${debate.agent1}</p>
                <p><strong>Agent 2:</strong> ${debate.agent2}</p>
                <p><strong>Contradiction Found:</strong> ${debate.contradiction}</p>
            `;
            historyContainer.appendChild(debateEntry);
        });
    } catch (error) {
        console.error("Error fetching debate history:", error);
    }
}

// Event listener for retrieving past debates
document.getElementById("fetch-debate-history").addEventListener("click", function () {
    const rule = document.getElementById("debate-rule").value;
    if (rule) {
        fetchDebateHistory(rule);
    } else {
        alert("Please enter a rule to fetch debate history.");
    }
});
