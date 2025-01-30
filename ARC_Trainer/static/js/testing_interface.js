document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ DOM fully loaded, initializing TestingInterface...");

    if (typeof ARCGrid === "undefined") {
        console.error("❌ Error: ARCGrid is not defined. Check if arc_grid.js is loading correctly.");
        return;
    }

    class TestingInterface {
        constructor() {
            this.correctAnswers = [];
            this.testPairs = [];

            this.initSymbolPicker();
            this.initButtons();
            this.loadRandomTask();
        }

        initSymbolPicker() {
            console.log("✅ Initializing symbol picker...");
            let symbolContainer = document.getElementById("symbol-picker");

            if (!symbolContainer) {
                console.error("❌ Error: Symbol picker container not found.");
                return;
            }

            symbolContainer.addEventListener("click", (event) => {
                if (event.target.classList.contains("symbol-btn")) {
                    let selectedSymbol = event.target.dataset.value;
                    let activeCells = document.querySelectorAll(".output-grid .grid-cell:focus");
                    activeCells.forEach(cell => {
                        cell.textContent = selectedSymbol;
                        cell.style.backgroundColor = this.getColorForValue(selectedSymbol);
                    });
                }
            });
        }

        initButtons() {
            document.getElementById("load-task-btn").addEventListener("click", () => this.loadRandomTask());
            document.getElementById("submit-task-btn").addEventListener("click", () => this.submitTask());
        }

        async loadRandomTask() {
            console.log("✅ Loading ARC Task...");

            try {
                let response = await fetch("/api/load-random-arc-task");
                let taskData = await response.json();

                console.log("✅ Loaded Task Data:", taskData);

                if (!taskData || !taskData.train || !taskData.test) {
                    alert("Invalid task data received");
                    return;
                }

                this.displayTrainingExamples(taskData.train);
                this.displayTestPairs(taskData.test);

            } catch (error) {
                console.error("❌ Error loading ARC task:", error);
                alert("Failed to load ARC task. Please try again.");
            }
        }

        displayTrainingExamples(trainExamples) {
            let trainContainer = document.getElementById("train-examples");
            trainContainer.innerHTML = "";

            trainExamples.forEach((pair, index) => {
                let pairWrapper = document.createElement("div");
                pairWrapper.classList.add("train-example-pair");

                let inputWrapper = this.createLabeledGrid(`train-input-${index}`, `Training Example ${index + 1} - Input`);
                let outputWrapper = this.createLabeledGrid(`train-output-${index}`, `Training Example ${index + 1} - Output`);

                pairWrapper.appendChild(inputWrapper);
                pairWrapper.appendChild(outputWrapper);
                trainContainer.appendChild(pairWrapper);

                if (typeof ARCGrid !== "undefined") {
                    let inputGrid = new ARCGrid(`train-input-${index}`);
                    inputGrid.renderGrid(pair.input);

                    let outputGrid = new ARCGrid(`train-output-${index}`);
                    outputGrid.renderGrid(pair.output);
                } else {
                    console.error("❌ Error: ARCGrid is not loaded before calling.");
                }
            });
        }

        displayTestPairs(testExamples) {
            let testContainer = document.getElementById("test-examples-container");
            testContainer.innerHTML = "";

            testExamples.forEach((pair, index) => {
                let pairDiv = document.createElement("div");
                pairDiv.classList.add("test-example-pair");

                let inputWrapper = this.createLabeledGrid(`test-input-${index}`, `Test Input ${index + 1}`);
                let outputWrapper = this.createLabeledGrid(`test-output-${index}`, `Expected Output ${index + 1}`);

                pairDiv.appendChild(inputWrapper);
                pairDiv.appendChild(outputWrapper);
                testContainer.appendChild(pairDiv);

                if (typeof ARCGrid !== "undefined") {
                    let inputGrid = new ARCGrid(`test-input-${index}`);
                    inputGrid.renderGrid(pair.input);

                    this.correctAnswers[index] = pair.output || [];

                    let outputGrid = new ARCGrid(`test-output-${index}`, true);
                    let emptyGrid = pair.output.map(row => row.map(() => 0));
                    outputGrid.renderGrid(emptyGrid);
                } else {
                    console.error("❌ Error: ARCGrid is not loaded before calling.");
                }
            });
        }

        createLabeledGrid(id, label) {
            let container = document.createElement("div");
            container.classList.add("grid-container-wrapper");

            let labelElement = document.createElement("h3");
            labelElement.textContent = label;

            let gridDiv = document.createElement("div");
            gridDiv.classList.add("grid-container");
            gridDiv.id = id;

            container.appendChild(labelElement);
            container.appendChild(gridDiv);

            return container;
        }

        async submitTask() {
            let outputData = [];
            document.querySelectorAll("#output-grid-container .grid-cell").forEach(cell => {
                outputData.push(cell.textContent.trim() || "0");
            });

            try {
                let response = await fetch("/api/process-arc-task", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ solution: outputData })
                });
                let data = await response.json();

                document.getElementById("ai-output").textContent = JSON.stringify(data.solution, null, 2);
                this.loadAIDebate();
                this.loadKnowledgeGraph();
            } catch (error) {
                console.error("Error submitting ARC task:", error);
                alert("Submission failed. Please try again.");
            }
        }

        async loadAIDebate() {
            try {
                let response = await fetch("/api/get-debate-history");
                let data = await response.json();
                let debateContainer = document.getElementById("debate-log");
                debateContainer.innerHTML = "";

                data.debate_log.forEach((debate) => {
                    let debateEntry = document.createElement("div");
                    debateEntry.classList.add("debate-entry");

                    debateEntry.innerHTML = `
                        <p><strong>Rule:</strong> ${debate.rule}</p>
                        <p><strong>Agent 1:</strong> ${debate.agent1}</p>
                        <p><strong>Agent 2:</strong> ${debate.agent2}</p>
                        <p><strong>Judge Decision:</strong> ${debate.judge}</p>
                        <p class="${debate.contradiction ? 'contradiction-highlight' : 'valid-highlight'}">
                            ${debate.contradiction ? "⚠ Contradiction Detected" : "✓ No Contradiction"}
                        </p>
                    `;
                    debateContainer.appendChild(debateEntry);
                });
            } catch (error) {
                console.error("Error loading AI debate:", error);
            }
        }

        getColorForValue(value) {
            const colors = {
                "0": "#ffffff", "1": "#000000", "2": "#ff4136", "3": "#2ecc40",
                "4": "#0074d9", "5": "#ffdc00", "6": "#f012be", "7": "#ff851b",
                "8": "#7fdbff", "9": "#870c25"
            };
            return colors[value] || "#ffffff";
        }
    }

    new TestingInterface();
});
