document.addEventListener("DOMContentLoaded", function () {
    console.log("📡 Fetching ARC task from API...");

    class ARCGrid {
        constructor(gridContainerId) {
            this.gridContainer = document.getElementById(gridContainerId);
            this.gridData = [];
        }

        renderGrid(data, editable = false) {
            if (!this.gridContainer) {
                console.error(`❌ Grid container with ID '${this.gridContainerId}' not found!`);
                return;
            }
            if (!data || data.length === 0) {
                console.error("❌ Attempted to render an empty grid.");
                return;
            }
            
            const rows = data.length;
            const cols = Math.max(...data.map(row => row.length));
            console.log(`📊 Rendering grid: ${rows} x ${cols}`);
            
            this.gridContainer.innerHTML = "";
            this.gridContainer.style.display = "grid";
            this.gridContainer.style.gridTemplateColumns = `repeat(${cols}, 40px)`;
            this.gridContainer.style.gridTemplateRows = `repeat(${rows}, 40px)`;
            this.gridContainer.style.gap = "2px";
            this.gridContainer.style.border = "2px solid black";
            
            this.gridData = data;

            this.gridData.forEach((row, rowIndex) => {
                row.forEach((cell, colIndex) => {
                    let div = document.createElement("div");
                    div.classList.add("grid-cell");
                    div.style.backgroundColor = getColorForValue(cell);
                    div.dataset.row = rowIndex;
                    div.dataset.col = colIndex;
                    div.style.width = "40px";
                    div.style.height = "40px";
                    div.style.border = "1px solid #000";
                    div.style.display = "flex";
                    div.style.alignItems = "center";
                    div.style.justifyContent = "center";
                    div.textContent = "";
                    if (editable) {
                        div.contentEditable = "true";
                        div.addEventListener("input", (event) => this.updateGridData(event));
                    }
                    this.gridContainer.appendChild(div);
                });
            });
        }

        updateGridData(event) {
            let cell = event.target;
            let row = parseInt(cell.dataset.row);
            let col = parseInt(cell.dataset.col);
            this.gridData[row][col] = cell.textContent.trim() || "0";
            cell.style.backgroundColor = getColorForValue(this.gridData[row][col]);
        }

        getGridData() {
            return this.gridData;
        }
    }

    function getColorForValue(value) {
        const colors = {
            "0": "#ffffff",
            "1": "#000000",
            "2": "#ff0000",
            "3": "#00ff00",
            "4": "#0000ff",
            "5": "#ffff00",
            "6": "#ff00ff",
            "7": "#00ffff",
            "8": "#808080"
        };
        return colors[value] || "#ffffff";
    }

    function loadRandomTask() {
        fetch("/api/load-random-arc-task")
            .then(response => response.json())
            .then(taskData => {
                console.log("📥 Loaded Task Data:", taskData);
                const trainContainer = document.getElementById("train-examples");
                trainContainer.innerHTML = "";

                taskData.train.forEach((example, index) => {
                    console.log(`📊 Training Example ${index + 1}: ${example.input.length}x${example.input[0].length}`);
                    let exampleWrapper = document.createElement("div");
                    exampleWrapper.classList.add("example-wrapper");

                    let inputTitle = document.createElement("h3");
                    inputTitle.textContent = `Training Example ${index + 1} - Input`;
                    exampleWrapper.appendChild(inputTitle);

                    let inputGrid = document.createElement("div");
                    inputGrid.id = `input-grid-${index}`;
                    inputGrid.classList.add("grid-container");
                    exampleWrapper.appendChild(inputGrid);

                    let outputTitle = document.createElement("h3");
                    outputTitle.textContent = `Training Example ${index + 1} - Expected Output`;
                    exampleWrapper.appendChild(outputTitle);

                    let outputGrid = document.createElement("div");
                    outputGrid.id = `output-grid-${index}`;
                    outputGrid.classList.add("grid-container");
                    exampleWrapper.appendChild(outputGrid);

                    trainContainer.appendChild(exampleWrapper);

                    new ARCGrid(`input-grid-${index}`).renderGrid(example.input);
                    new ARCGrid(`output-grid-${index}`).renderGrid(example.output);
                });
            })
            .catch(error => console.error("Error loading ARC task:", error));
    }

    function submitTask() {
        let outputData = outputGrid.getGridData();
        console.log("📤 Submitting Test Grid Data:", outputData);
        fetch("/api/process-arc-task", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ task: outputData })
        })
        .then(response => response.json())
        .then(data => {
            console.log("✅ AI Response Received:", data);
            document.getElementById("ai-output").textContent = JSON.stringify(data.solution, null, 2);
        })
        .catch(error => console.error("Error submitting ARC task:", error));
    }

    document.getElementById("load-task-btn").addEventListener("click", loadRandomTask);
    document.getElementById("submit-task-btn").addEventListener("click", submitTask);

    // Load first task automatically
    loadRandomTask();
});