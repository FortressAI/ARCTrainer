document.addEventListener("DOMContentLoaded", function () {
    class HomeInterface {
        constructor() {
            this.initButtons();
        }

        initButtons() {
            let loadTaskBtn = document.getElementById("load-task-btn");
            let submitTaskBtn = document.getElementById("submit-task-btn");
            let startDebateBtn = document.getElementById("start-debate-btn");
            let approveBtn = document.getElementById("approve-btn");
            let rejectBtn = document.getElementById("reject-btn");

            if (loadTaskBtn) loadTaskBtn.addEventListener("click", () => this.loadTask());
            if (submitTaskBtn) submitTaskBtn.addEventListener("click", () => this.submitTask());
            if (startDebateBtn) startDebateBtn.addEventListener("click", () => this.startAIDebate());
            if (approveBtn) approveBtn.addEventListener("click", () => this.approveSolution());
            if (rejectBtn) rejectBtn.addEventListener("click", () => this.rejectSolution());
        }

        loadTask() {
            fetch("/api/load-random-arc-task")
            .then(response => response.json())
            .then(data => {
                document.getElementById("task-demo-grid").textContent = JSON.stringify(data, null, 2);
            })
            .catch(error => console.error("Error loading ARC task:", error));
        }

        submitTask() {
            let outputData = document.querySelectorAll("#test-grid-container .grid-cell");
            let taskData = Array.from(outputData).map(cell => cell.style.backgroundColor || "#ffffff");
            
            fetch("/api/process-arc-task", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ task: taskData })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("ai-output").textContent = JSON.stringify(data.solution, null, 2);
            })
            .catch(error => console.error("Error submitting ARC task:", error));
        }

        startAIDebate() {
            fetch("/api/start-ai-debate")
            .then(response => response.json())
            .then(data => {
                document.getElementById("debate-log").textContent = JSON.stringify(data.debate_log, null, 2);
            })
            .catch(error => console.error("Error starting AI debate:", error));
        }

        approveSolution() {
            alert("Solution Approved!");
            fetch("/api/approve-solution", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ status: "approved" })
            });
        }

        rejectSolution() {
            alert("Solution Rejected!");
            fetch("/api/reject-solution", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ status: "rejected" })
            });
        }
    }

    new HomeInterface();
});
