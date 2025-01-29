document.addEventListener("DOMContentLoaded", function () {
    class TestingInterface {
        constructor() {
            this.initButtons();
            this.initSymbolPicker();
        }

        initButtons() {
            let loadBtn = document.getElementById("load-task-btn");
            let submitBtn = document.getElementById("submit-task-btn");
            let approveBtn = document.getElementById("approve-btn");
            let rejectBtn = document.getElementById("reject-btn");
            let modifyBtn = document.getElementById("modify-btn");

            if (loadBtn) loadBtn.addEventListener("click", () => this.loadRandomTask());
            if (submitBtn) submitBtn.addEventListener("click", () => this.submitTask());
            if (approveBtn) approveBtn.addEventListener("click", () => this.validateReasoning("approved"));
            if (rejectBtn) rejectBtn.addEventListener("click", () => this.validateReasoning("rejected"));
            if (modifyBtn) modifyBtn.addEventListener("click", () => this.modifyTask());
        }

        initSymbolPicker() {
            let symbolContainer = document.getElementById("symbol-container");
            if (symbolContainer) {
                symbolContainer.addEventListener("click", function(event) {
                    if (event.target.classList.contains("symbol-option")) {
                        let selectedSymbol = event.target.textContent;
                        let activeCells = document.querySelectorAll("#output-grid-container .grid-cell:focus");
                        activeCells.forEach(cell => cell.textContent = selectedSymbol);
                    }
                });
            }
        }

        loadRandomTask() {
            fetch("/api/load-random-arc-task")
            .then(response => response.json())
            .then(data => {
                document.getElementById("demo-container").textContent = JSON.stringify(data, null, 2);
            })
            .catch(error => console.error("Error loading ARC task:", error));
        }

        submitTask() {
            let outputData = [];
            document.querySelectorAll("#output-grid-container .grid-cell").forEach(cell => {
                outputData.push(cell.textContent.trim() || "0");
            });
            
            fetch("/api/process-arc-task", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ task: outputData })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("ai-output").textContent = JSON.stringify(data.solution, null, 2);
                this.loadAIDebate();
                this.loadKnowledgeGraph();
            })
            .catch(error => console.error("Error submitting ARC task:", error));
        }

        loadAIDebate() {
            fetch("/api/get-debate-history")
            .then(response => response.json())
            .then(data => {
                document.getElementById("debate-log").textContent = JSON.stringify(data.debate_log, null, 2);
            });
        }

        loadKnowledgeGraph() {
            fetch("/api/get-knowledge-graph")
            .then(response => response.json())
            .then(data => {
                document.getElementById("kg-visual").textContent = JSON.stringify(data, null, 2);
            });
        }

        validateReasoning(decision) {
            fetch("/api/validate-reasoning", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ decision: decision })
            })
            .then(response => response.json())
            .then(data => {
                alert("Decision recorded: " + decision);
            });
        }

        modifyTask() {
            let outputGridCells = document.querySelectorAll("#output-grid-container .grid-cell");
            outputGridCells.forEach(cell => cell.contentEditable = "true");
            alert("Grid is now editable for modifications.");
        }
    }

    new TestingInterface();
});