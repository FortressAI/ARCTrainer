document.addEventListener("DOMContentLoaded", function() {
    class TestingInterface {
        constructor() {
            this.correctAnswer = null; // Store correct output for validation
            this.initButtons();
            this.initSymbolPicker();
        }

        initButtons() {
            let loadBtn = document.getElementById("load-task-btn");
            let submitBtn = document.getElementById("submit-task-btn");
            let approveBtn = document.getElementById("approve-btn");
            let rejectBtn = document.getElementById("reject-btn");

            if (loadBtn) loadBtn.addEventListener("click", () => this.loadRandomTask());
            if (submitBtn) submitBtn.addEventListener("click", () => this.submitTask());
            if (approveBtn) approveBtn.addEventListener("click", () => this.validateReasoning("approved"));
            if (rejectBtn) rejectBtn.addEventListener("click", () => this.validateReasoning("rejected"));
        }

        initSymbolPicker() {
            let symbolContainer = document.getElementById("symbol-picker");
            if (symbolContainer) {
                symbolContainer.addEventListener("click", (event) => {
                    if (event.target.classList.contains("symbol-btn")) {
                        let selectedSymbol = event.target.dataset.value;
                        let activeCells = document.querySelectorAll("#output-grid-container .grid-cell:focus");
                        activeCells.forEach(cell => {
                            cell.textContent = selectedSymbol;
                            cell.style.backgroundColor = getColorForValue(selectedSymbol);
                        });
                    }
                });
            }
        }

        loadRandomTask() {
            fetch("/api/load-random-arc-task")
            .then(response => response.json())
            .then(taskData => {
                if (!taskData || !taskData.test || !taskData.test[0].input) {
                    alert("Invalid task data received");
                    return;
                }
                
                let inputGrid = new ARCGrid("test-grid-container");
                inputGrid.renderGrid(taskData.test[0].input);

                // Store correct output answer but do not display it
                this.correctAnswer = taskData.test[0].output;

                // Create a blank output grid that matches the answer size
                let outputGrid = new ARCGrid("output-grid-container", true);
                let emptyGrid = this.correctAnswer.map(row => row.map(() => 0));
                outputGrid.renderGrid(emptyGrid);
            })
            .catch(error => {
                console.error("Error loading ARC task:", error);
                alert("Failed to load ARC task. Please try again.");
            });
        }

        submitTask() {
            let outputGrid = document.getElementById("output-grid-container");
            if (!outputGrid) {
                alert("Output grid is missing.");
                return;
            }

            let gridCells = outputGrid.getElementsByClassName("grid-cell");
            let solution = [];
            let rowSize = parseInt(outputGrid.style.gridTemplateColumns.split(" ").length);
            let rowData = [];

            for (let i = 0; i < gridCells.length; i++) {
                let value = parseInt(gridCells[i].textContent.trim()) || 0;
                rowData.push(value);
                if ((i + 1) % rowSize === 0) {
                    solution.push(rowData);
                    rowData = [];
                }
            }
            
            let isCorrect = JSON.stringify(solution) === JSON.stringify(this.correctAnswer);

            fetch("/api/process-arc-task", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ solution: solution, correct: isCorrect })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("ai-output").textContent = JSON.stringify(data.solution, null, 2);
                this.loadAIDebate();
                this.loadKnowledgeGraph();
            })
            .catch(error => {
                console.error("Error submitting ARC task:", error);
                alert("Submission failed. Please try again.");
            });
        }

        loadAIDebate() {
            fetch("/api/get-debate-history")
            .then(response => response.json())
            .then(data => {
                document.getElementById("debate-log").textContent = JSON.stringify(data.debate_log, null, 2);
            })
            .catch(error => {
                console.error("Error loading debate history:", error);
            });
        }

        loadKnowledgeGraph() {
            fetch("/api/get-knowledge-graph")
            .then(response => response.json())
            .then(data => {
                document.getElementById("kg-visual").textContent = JSON.stringify(data, null, 2);
            })
            .catch(error => {
                console.error("Error loading knowledge graph:", error);
            });
        }

        validateReasoning(decision) {
            fetch("/api/validate-reasoning", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ decision: decision })
            })
            .then(response => response.json())
            .then(() => {
                alert("Decision recorded: " + decision);
            })
            .catch(error => {
                console.error("Error validating reasoning:", error);
                alert("Validation failed. Try again.");
            });
        }
    }

    function getColorForValue(value) {
        const colors = {
            "0": "#ffffff", "1": "#000000", "2": "#ff4136", "3": "#2ecc40",
            "4": "#0074d9", "5": "#ffdc00", "6": "#f012be", "7": "#ff851b",
            "8": "#7fdbff", "9": "#870c25"
        };
        return colors[value] || "#ffffff";
    }

    new TestingInterface();
});
