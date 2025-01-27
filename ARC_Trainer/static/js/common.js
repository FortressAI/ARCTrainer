document.addEventListener("DOMContentLoaded", function() {
    class TestingInterface {
        constructor() {
            this.initButtons();
        }

        initButtons() {
            document.getElementById("load-task-btn").addEventListener("click", () => this.loadTask());
            document.getElementById("submit-task-btn").addEventListener("click", () => this.submitTask());
            document.getElementById("approve-btn").addEventListener("click", () => this.validateReasoning("approved"));
            document.getElementById("reject-btn").addEventListener("click", () => this.validateReasoning("rejected"));
            document.getElementById("modify-btn").addEventListener("click", () => this.modifyTask());
        }

        loadTask() {
            let fileInput = document.getElementById("load-task-file");
            let file = fileInput.files[0];
            if (!file) return UIHelpers.showAlert("Please select a task file.", "error");

            let reader = new FileReader();
            reader.onload = function(e) {
                let taskData = JSON.parse(e.target.result);
                renderTaskGrid(taskData);
            };
            reader.readAsText(file);
        }

        submitTask() {
            let outputData = [];
            document.querySelectorAll("#output-grid-container .grid-cell").forEach(cell => {
                outputData.push(cell.textContent.trim() || "0");
            });

            ARC.submitSolution(outputData)
            .then(data => {
                document.getElementById("ai-output").textContent = JSON.stringify(data.solution, null, 2);
                this.loadAIDebate();
                this.loadKnowledgeGraph();
                this.checkRLMValidation(data.solution);
            });
        }

        loadAIDebate() {
            API.request("/api/get-debate-history")
            .then(data => {
                document.getElementById("debate-log").textContent = JSON.stringify(data.debate_log, null, 2);
            });
        }

        loadKnowledgeGraph() {
            KnowledgeGraph.fetchGraph()
            .then(data => {
                document.getElementById("kg-visual").textContent = JSON.stringify(data, null, 2);
            });
        }

        checkRLMValidation(solution) {
            API.request("/api/validate-rlm-reasoning", "POST", { solution: solution })
            .then(data => {
                document.getElementById("rlm-validation").textContent = `RLM Validation: ${data.status}`;
            })
            .catch(error => {
                Logger.error("RLM Validation Error:", error);
                UIHelpers.showAlert("Failed to validate reasoning with RLM.", "error");
            });
        }

        validateReasoning(decision) {
            API.request("/api/validate-reasoning", "POST", { decision: decision })
            .then(data => {
                UIHelpers.showAlert("Decision recorded: " + decision, "success");
            });
        }

        modifyTask() {
            let outputGridCells = document.querySelectorAll("#output-grid-container .grid-cell");
            outputGridCells.forEach(cell => cell.contentEditable = "true");
            UIHelpers.showAlert("Grid is now editable for modifications.", "info");
        }
    }

    new TestingInterface();
});
