document.addEventListener("DOMContentLoaded", function () {
    class GridRenderer {
        constructor(containerId) {
            this.gridContainer = document.getElementById(containerId);
            if (!this.gridContainer) {
                console.error(`❌ Grid container with ID '${containerId}' not found!`);
                return;
            }
            this.gridData = [];
        }

        renderGrid(gridSize, data = null, editable = false) {
            if (!this.gridContainer) return;
            this.gridContainer.innerHTML = "";
            this.gridContainer.style.gridTemplateColumns = `repeat(${gridSize}, 40px)`;
            this.gridData = data || Array.from({ length: gridSize }, () => Array(gridSize).fill(0));

            this.gridData.forEach((row, rowIndex) => {
                row.forEach((cell, colIndex) => {
                    let div = document.createElement("div");
                    div.classList.add("grid-cell");
                    div.textContent = cell;
                    div.dataset.row = rowIndex;
                    div.dataset.col = colIndex;
                    if (editable) div.contentEditable = "true";
                    div.addEventListener("input", (event) => this.updateGridData(event));
                    this.gridContainer.appendChild(div);
                });
            });
        }

        updateGridData(event) {
            let cell = event.target;
            let row = parseInt(cell.dataset.row);
            let col = parseInt(cell.dataset.col);
            this.gridData[row][col] = cell.textContent.trim() || "0";
        }

        getGridData() {
            return this.gridData;
        }
    }

    const inputGrid = new GridRenderer("input-grid-container");
    const outputGrid = new GridRenderer("output-grid-container");

    document.getElementById("load-task-btn").addEventListener("click", function() {
        let fileInput = document.getElementById("load-task-file");
        let file = fileInput.files[0];
        if (!file) return alert("Please select a task file.");

        let reader = new FileReader();
        reader.onload = function(e) {
            let taskData = JSON.parse(e.target.result);
            inputGrid.renderGrid(taskData.train[0].input.length, taskData.train[0].input);
            outputGrid.renderGrid(taskData.train[0].input.length, null, true);
        };
        reader.readAsText(file);
    });

    document.getElementById("submit-task-btn").addEventListener("click", function() {
        let outputData = outputGrid.getGridData();
        fetch("/api/process-arc-task", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ task: outputData })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("ai-output").textContent = JSON.stringify(data.solution, null, 2);
        });
    });

    if (inputGrid.gridContainer) inputGrid.renderGrid(5, null, false);
    if (outputGrid.gridContainer) outputGrid.renderGrid(5, null, true);
});