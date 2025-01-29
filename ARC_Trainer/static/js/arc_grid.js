document.addEventListener("DOMContentLoaded", function () {
    console.log("📡 Fetching ARC task from API...");

    class ARCGrid {
        constructor(gridContainerId) {
            this.gridContainer = document.getElementById(gridContainerId);
            this.gridData = [];
        }

        validateGrid(data) {
            if (!Array.isArray(data) || data.length === 0 || !Array.isArray(data[0])) {
                console.error("❌ Invalid grid format.");
                return false;
            }
            const rowLength = data[0].length;
            return data.every(row => Array.isArray(row) && row.length === rowLength);
        }

        renderGrid(data, editable = false) {
            if (!this.gridContainer) {
                console.error(`❌ Grid container with ID '${this.gridContainerId}' not found!`);
                return;
            }
            if (!this.validateGrid(data)) {
                console.error("❌ Grid data is not structured correctly.");
                return;
            }
            
            const rows = data.length;
            const cols = Math.max(...data.map(row => row.length));
            console.log(`📊 Rendering grid: ${rows} x ${cols}`);
            
            this.gridContainer.innerHTML = "";
            this.gridContainer.style.display = "grid";
            this.gridContainer.style.gridTemplateColumns = `repeat(${cols}, 30px)`;
            this.gridContainer.style.gridTemplateRows = `repeat(${rows}, 30px)`;
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
                    div.style.width = "30px";
                    div.style.height = "30px";
                    div.style.border = "1px solid #000";
                    div.style.display = "flex";
                    div.style.alignItems = "center";
                    div.style.justifyContent = "center";
                    div.style.fontSize = "12px";
                    div.textContent = cell;
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
            let value = parseInt(cell.textContent.trim());
            if (isNaN(value) || value < 0 || value > 9) {
                cell.textContent = "0";
                value = 0;
            }
            this.gridData[row][col] = value;
            cell.style.backgroundColor = getColorForValue(value);
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
            "8": "#808080",
            "9": "#a52a2a"
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

                    let inputContainer = document.createElement("div");
                    inputContainer.innerHTML = `<div class='example-title'>Input</div><div id='input-grid-${index}' class='grid-container'></div>`;

                    let outputContainer = document.createElement("div");
                    outputContainer.innerHTML = `<div class='example-title'>Expected Output</div><div id='output-grid-${index}' class='grid-container'></div>`;

                    exampleWrapper.appendChild(inputContainer);
                    exampleWrapper.appendChild(outputContainer);
                    trainContainer.appendChild(exampleWrapper);

                    new ARCGrid(`input-grid-${index}`).renderGrid(example.input);
                    new ARCGrid(`output-grid-${index}`).renderGrid(example.output);
                });
            })
            .catch(error => console.error("Error loading ARC task:", error));
    }

    document.getElementById("load-task-btn").addEventListener("click", loadRandomTask);
    loadRandomTask();
});
