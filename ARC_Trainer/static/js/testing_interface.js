document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ DOM fully loaded, initializing TestingInterface...");

    class TestingInterface {
        constructor() {
            this.initButtons();
            this.loadRandomTask();
        }

        initButtons() {
            let loadBtn = document.getElementById("load-task-btn");
            let submitBtn = document.getElementById("submit-task-btn");

            if (loadBtn) {
                loadBtn.addEventListener("click", () => this.loadRandomTask());
            }
            if (submitBtn) {
                submitBtn.addEventListener("click", () => this.submitSolution());
            }
        }

        async loadRandomTask() {
            try {
                let response = await fetch("/api/load-random-arc-task");
                if (!response.ok) throw new Error(`Server responded with ${response.status}`);
                let data = await response.json();

                // data will include: 
                //   name, train, test, correct_solutions
                console.log("Loaded ARC Task Data:", data);

                // Clear out old grids
                document.getElementById("train-examples").innerHTML = "";
                document.getElementById("test-examples-container").innerHTML = "";
                document.getElementById("ai-output").textContent = "";

                this.displayTrainExamples(data.train);
                this.displayTestExamples(data.test, data.correct_solutions);
            } catch (error) {
                console.error("❌ Error loading random task:", error);
                alert("Failed to load random task. Check console for details.");
            }
        }

        displayTrainExamples(trainList) {
            let trainContainer = document.getElementById("train-examples");
            if (!trainContainer) return;

            trainList.forEach((pair, idx) => {
                // Create wrappers
                let exampleWrapper = document.createElement("div");
                exampleWrapper.classList.add("train-example-pair");

                // Input grid
                let inputDiv = document.createElement("div");
                let inputTitle = document.createElement("h4");
                inputTitle.textContent = `Train Example ${idx + 1} - Input`;
                let inputGridDiv = document.createElement("div");
                let inputGridId = `train-input-grid-${idx}`;
                inputGridDiv.id = inputGridId;
                inputDiv.appendChild(inputTitle);
                inputDiv.appendChild(inputGridDiv);

                // Output grid
                let outputDiv = document.createElement("div");
                let outputTitle = document.createElement("h4");
                outputTitle.textContent = `Train Example ${idx + 1} - Output`;
                let outputGridDiv = document.createElement("div");
                let outputGridId = `train-output-grid-${idx}`;
                outputGridDiv.id = outputGridId;
                outputDiv.appendChild(outputTitle);
                outputDiv.appendChild(outputGridDiv);

                exampleWrapper.appendChild(inputDiv);
                exampleWrapper.appendChild(outputDiv);
                trainContainer.appendChild(exampleWrapper);

                // Render with ARCGrid
                if (window.ARCGrid) {
                    let inputGrid = new ARCGrid(inputGridId, false);
                    inputGrid.renderGrid(pair.input);

                    let outputGrid = new ARCGrid(outputGridId, false);
                    outputGrid.renderGrid(pair.output);
                }
            });
        }

        displayTestExamples(testList, correctSolutions) {
            let testContainer = document.getElementById("test-examples-container");
            if (!testContainer) return;

            testList.forEach((pair, idx) => {
                let pairWrapper = document.createElement("div");
                pairWrapper.classList.add("test-example-pair");

                // Test Input
                let inputDiv = document.createElement("div");
                let inputTitle = document.createElement("h4");
                inputTitle.textContent = `Test Input ${idx + 1}`;
                let inputGridDiv = document.createElement("div");
                let inputGridId = `test-input-grid-${idx}`;
                inputGridDiv.id = inputGridId;
                inputDiv.appendChild(inputTitle);
                inputDiv.appendChild(inputGridDiv);

                // User Attempt
                let userAttemptDiv = document.createElement("div");
                let userAttemptTitle = document.createElement("h4");
                userAttemptTitle.textContent = `Your Attempt ${idx + 1}`;
                let userAttemptGridDiv = document.createElement("div");
                let userAttemptGridId = `test-attempt-grid-${idx}`;
                userAttemptGridDiv.id = userAttemptGridId;
                userAttemptDiv.appendChild(userAttemptTitle);
                userAttemptDiv.appendChild(userAttemptGridDiv);

                pairWrapper.appendChild(inputDiv);
                pairWrapper.appendChild(userAttemptDiv);
                testContainer.appendChild(pairWrapper);

                // If we do have correctSolutions:
                if (correctSolutions && correctSolutions[idx]) {
                    let correctDiv = document.createElement("div");
                    let correctTitle = document.createElement("h4");
                    correctTitle.textContent = `Correct Solution ${idx + 1}`;
                    let correctGridDiv = document.createElement("div");
                    let correctGridId = `test-correct-grid-${idx}`;
                    correctGridDiv.id = correctGridId;
                    correctDiv.appendChild(correctTitle);
                    correctDiv.appendChild(correctGridDiv);
                    pairWrapper.appendChild(correctDiv);
                }

                // Render with ARCGrid
                if (window.ARCGrid) {
                    // Input
                    let inputGrid = new ARCGrid(inputGridId, false);
                    inputGrid.renderGrid(pair.input);

                    // Attempt (editable)
                    let userGrid = new ARCGrid(userAttemptGridId, true);
                    // Start with an empty or zeroed grid of same shape
                    let emptyGrid = pair.input.map(row => row.map(() => 0));
                    userGrid.renderGrid(emptyGrid);

                    // Correct
                    if (correctSolutions && correctSolutions[idx]) {
                        let correctGrid = new ARCGrid(`test-correct-grid-${idx}`, false);
                        correctGrid.renderGrid(correctSolutions[idx]);
                    }
                }
            });
        }

        submitSolution() {
            // Example of collecting the user attempt from the first test pair only
            let userSolution = [];
            let attemptGrid = document.getElementById("test-attempt-grid-0");
            if (!attemptGrid) {
                alert("No test attempt grid found to submit!");
                return;
            }

            let cells = attemptGrid.querySelectorAll(".grid-cell");
            if (!cells.length) {
                alert("No cells in user attempt grid!");
                return;
            }

            // Determine row/col from styling
            let columns = parseInt(attemptGrid.style.gridTemplateColumns.split(" ").length);
            let rows = cells.length / columns;

            let rowData = [];
            for (let i = 0; i < cells.length; i++) {
                let val = cells[i].textContent.trim() || "0";
                // convert to int
                let numVal = parseInt(val);
                rowData.push(isNaN(numVal) ? 0 : numVal);
                if ((i + 1) % columns === 0) {
                    userSolution.push(rowData);
                    rowData = [];
                }
            }

            const payload = {
                task_name: "default_task", // or whatever we loaded
                solution: userSolution
            };

            fetch("/api/process-arc-task", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                console.log("Process ARC Task result:", data);
                // Show AI solution in the #ai-output container
                document.getElementById("ai-output").textContent = JSON.stringify(data.solution, null, 2);
            })
            .catch(error => {
                console.error("Error submitting solution:", error);
                alert("Failed to submit solution. Check console.");
            });
        }
    }

    // Initialize
    new TestingInterface();
});
