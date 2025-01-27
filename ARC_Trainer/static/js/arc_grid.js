document.addEventListener("DOMContentLoaded", function() {
    class ARCGrid {
        constructor(gridContainerId) {
            this.gridContainer = document.getElementById(gridContainerId);
            this.gridData = [];
        }

        renderGrid(gridSize, data = null, editable = false) {
            this.gridContainer.innerHTML = "";
            this.gridContainer.style.gridTemplateColumns = `repeat(${gridSize}, 40px)`;
            this.gridData = data || Array(gridSize).fill().map(() => Array(gridSize).fill(0));

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

    const inputGrid = new ARCGrid("input-grid-container");
    const outputGrid = new ARCGrid("output-grid-container");

    document.getElementById("load-task-btn").addEventListener("click", function() {
        let fileInput = document.getElementById("load-task-file");
        let file = fileInput.files[0];
        if (!file) return UIHelpers.showAlert("Please select a task file.", "error");

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
        ARC.submitSolution(outputData)
        .then(data => {
            document.getElementById("ai-output").textContent = JSON.stringify(data.solution, null, 2);
        });
    });
});