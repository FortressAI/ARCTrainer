document.addEventListener("DOMContentLoaded", function () {
    let testIndex = 0;

    function createGrid(height, width, containerId, isEditable = false) {
        let gridContainer = document.getElementById(containerId);
        gridContainer.innerHTML = ""; // Clear previous grid
        gridContainer.style.display = "grid";
        gridContainer.style.gridTemplateColumns = `repeat(${width}, 1fr)`;

        for (let i = 0; i < height; i++) {
            for (let j = 0; j < width; j++) {
                let cell = document.createElement("div");
                cell.classList.add("grid-cell", "cell-0"); // Default empty cell
                cell.setAttribute("data-x", i);
                cell.setAttribute("data-y", j);
                
                if (isEditable) {
                    cell.addEventListener("click", function () {
                        cycleCellColor(cell);
                    });
                }

                gridContainer.appendChild(cell);
            }
        }
    }

    function loadTaskGrid(taskData) {
        if (!taskData || !taskData.train || !taskData.test) {
            console.error("Invalid task data:", taskData);
            return;
        }

        let height = taskData.train[0].input.length;
        let width = taskData.train[0].input[0].length;

        // Example Task Grid (Training Examples)
        createGrid(height, width, "task-demo-grid");
        fillGrid(taskData.train[0].input, "task-demo-grid");

        // Test Input Grid
        createGrid(height, width, "test-input-grid");
        fillGrid(taskData.test[testIndex].input, "test-input-grid");

        // User Editable Grid
        createGrid(height, width, "submission-grid", true);
    }

    function fillGrid(data, containerId) {
        let gridCells = document.querySelectorAll(`#${containerId} .grid-cell`);
        let width = data[0].length;

        for (let i = 0; i < data.length; i++) {
            for (let j = 0; j < width; j++) {
                let symbol = data[i][j];
                let index = i * width + j;
                if (gridCells[index]) {
                    gridCells[index].className = `grid-cell cell-${symbol}`;
                }
            }
        }
    }

    function cycleCellColor(cell) {
        let currentClass = cell.classList[1]; // Get second class (color class)
        let currentColorIndex = parseInt(currentClass.split("-")[1]);

        let nextColorIndex = (currentColorIndex + 1) % 10; // Cycle through 0-9 colors
        cell.className = `grid-cell cell-${nextColorIndex}`;
    }

    function nextTestInput() {
        testIndex++;
        document.getElementById("load-arc-task").click();
    }

    function copyFromInput() {
        let sourceGrid = document.querySelectorAll("#test-input-grid .grid-cell");
        let targetGrid = document.querySelectorAll("#submission-grid .grid-cell");

        sourceGrid.forEach((cell, index) => {
            let symbol = cell.classList[1]; // Get color class
            targetGrid[index].className = `grid-cell ${symbol}`;
        });
    }

    function resetOutputGrid() {
        document.getElementById("submission-grid").innerHTML = "";
    }

    function submitSolution() {
        let cells = document.querySelectorAll("#submission-grid .grid-cell");
        let gridData = [];

        let width = document.querySelector("#submission-grid").style.gridTemplateColumns.split(" ").length;
        let rowData = [];

        cells.forEach((cell, index) => {
            let symbol = parseInt(cell.classList[1].split("-")[1]);
            rowData.push(symbol);
            if ((index + 1) % width === 0) {
                gridData.push(rowData);
                rowData = [];
            }
        });

        fetch("/api/submit-solution", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ solution: gridData })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(error => console.error("Error submitting solution:", error));
    }

    // Auto-load the first task
    fetch("/api/load-arc-task?task_name=default_task")
        .then(response => response.json())
        .then(data => {
            loadTaskGrid(data);
        })
        .catch(error => console.error("Error loading task:", error));

    document.getElementById("next-test-input").addEventListener("click", nextTestInput);
    document.getElementById("copy-from-input").addEventListener("click", copyFromInput);
    document.getElementById("reset-grid").addEventListener("click", resetOutputGrid);
    document.getElementById("submit-solution").addEventListener("click", submitSolution);
});
