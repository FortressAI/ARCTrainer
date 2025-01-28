document.addEventListener("DOMContentLoaded", function () {
    console.log("📡 Fetching ARC task from API...");

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

    function loadRandomTask() {
        fetch("/api/load-random-arc-task")
            .then(response => response.json())
            .then(taskData => {
                console.log("Loaded task:", taskData);
                inputGrid.renderGrid(taskData.train[0].input.length, taskData.train[0].input, false);
                outputGrid.renderGrid(taskData.train[0].input.length, null, true);
            })
            .catch(error => console.error("Error loading ARC task:", error));
    }

    function submitTask() {
        let outputData = outputGrid.getGridData();
        fetch("/api/process-arc-task", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ task: outputData })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("ai-output").textContent = JSON.stringify(data.solution, null, 2);
            console.log("Task completed:", data);
            setTimeout(loadRandomTask, 2000); // Auto-load next task after 2 sec delay
        })
        .catch(error => console.error("Error submitting ARC task:", error));
    }

    const loadTaskBtn = document.getElementById("load-task-btn");
    const submitTaskBtn = document.getElementById("submit-task-btn");

    if (loadTaskBtn) {
        loadTaskBtn.addEventListener("click", loadRandomTask);
    } else {
        console.error("❌ load-task-btn element is missing!");
    }

    if (submitTaskBtn) {
        submitTaskBtn.addEventListener("click", submitTask);
    } else {
        console.error("❌ submit-task-btn element is missing!");
    }

    // Auto-load the first task on page load
    loadRandomTask();
});