document.addEventListener("DOMContentLoaded", function () {
    class DebateHistory {
        constructor() {
            this.loadDebateHistory();
            this.loadHumanValidationQueue();
            this.initDebateButton();
        }

        initDebateButton() {
            let startDebateBtn = document.getElementById("start-debate");
            if (startDebateBtn) {
                startDebateBtn.addEventListener("click", async () => {
                    try {
                        let response = await fetch("/api/start-debate", { method: "POST" });
                        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
                        let data = await response.json();
                        this.displayDebateResults(data);
                    } catch (error) {
                        console.error("Error starting debate:", error);
                        alert("Failed to start debate. Please try again.");
                    }
                });
            }
        }

        async loadDebateHistory() {
            try {
                let response = await fetch("/api/get-debate-history");
                if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
                let data = await response.json();
                document.getElementById("debate-log").textContent = JSON.stringify(data.debate_log, null, 2);
            } catch (error) {
                console.error("Error loading debate history:", error);
                alert("Failed to load debate history.");
            }
        }

        async loadHumanValidationQueue() {
            try {
                let response = await fetch("/api/human-validation-queue");
                if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
                let data = await response.json();
                let queueElement = document.getElementById("human-validation-queue");
                if (queueElement) {
                    queueElement.textContent = JSON.stringify(data.queue, null, 2);
                } else {
                    console.warn("Warning: #human-validation-queue element not found in HTML.");
                }
            } catch (error) {
                console.error("Error loading human validation queue:", error);
                alert("Failed to load human validation queue.");
            }
        }
    }

    new DebateHistory();
});
