document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ arc_grid.js is loaded.");

    class ARCGrid {
        constructor(gridContainerId, editable = false) {
            this.gridContainer = document.getElementById(gridContainerId);
            
            if (!this.gridContainer) {
                console.error(`❌ Error: Grid container '${gridContainerId}' not found.`);
                return;
            }
            
            this.gridData = [];
            this.editable = editable;
            this.activeSymbol = "0";
            this.initSymbolPicker();
        }

        renderGrid(data) {
            if (!this.gridContainer) {
                console.error(`❌ Error: Cannot render grid. Container '${this.gridContainer.id}' not found.`);
                return;
            }
            this.gridContainer.innerHTML = "";
            this.gridContainer.style.display = "grid";
            this.gridContainer.style.gridTemplateColumns = `repeat(${data[0].length}, 30px)`;
            this.gridContainer.style.gap = "2px";
            this.gridData = data;

            this.gridData.forEach((row, rowIndex) => {
                row.forEach((cell, colIndex) => {
                    let div = document.createElement("div");
                    div.classList.add("grid-cell");
                    div.style.backgroundColor = getColorForValue(cell);
                    div.dataset.row = rowIndex;
                    div.dataset.col = colIndex;
                    div.textContent = this.editable ? "" : cell;
                    if (this.editable) {
                        div.contentEditable = "true";
                        div.addEventListener("click", () => this.setCellValue(div));
                    }
                    this.gridContainer.appendChild(div);
                });
            });
        }

        setCellValue(cell) {
            cell.textContent = this.activeSymbol;
            cell.style.backgroundColor = getColorForValue(this.activeSymbol);
        }

        getGridData() {
            return this.gridData;
        }

        initSymbolPicker() {
            document.querySelectorAll(".symbol-btn").forEach(btn => {
                btn.addEventListener("click", (event) => {
                    this.activeSymbol = event.target.dataset.value;
                });
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

    async function loadRandomTask() {
        console.log("✅ Loading ARC Task...");

        try {
            let response = await fetch("/api/load-random-arc-task");
            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}`);
            }
            let taskData = await response.json();

            console.log("✅ Loaded Task Data:", taskData);
            if (!taskData || !taskData.train || !taskData.test) {
                alert("⚠️ Task data is missing or incorrectly formatted.");
                return;
            }

            // Ensure grid elements exist before trying to create ARCGrid
            let testContainer = document.getElementById("test-grid-container");
            let outputContainer = document.getElementById("output-grid-container");

            if (!testContainer || !outputContainer) {
                console.error("❌ Grid containers are missing from the DOM.");
                return;
            }

            let inputGrid = new ARCGrid("test-grid-container");
            if (inputGrid.gridContainer) inputGrid.renderGrid(taskData.test[0].input);

            let outputGrid = new ARCGrid("output-grid-container", true);
            if (outputGrid.gridContainer) {
                let emptyGrid = taskData.test[0].output.map(row => row.map(() => ""));
                outputGrid.renderGrid(emptyGrid);
            }

        } catch (error) {
            console.error("❌ Error loading ARC task:", error);
            alert("⚠️ Unable to load ARC task. Please check the server connection.");
        }
    }

    function submitSolution() {
        let outputGrid = document.getElementById("output-grid-container");
        if (!outputGrid) {
            alert("⚠️ Output grid is missing.");
            return;
        }

        let gridCells = outputGrid.getElementsByClassName("grid-cell");
        let solution = [];
        let rowData = [];
        let gridSize = outputGrid.style.gridTemplateColumns.split(" ").length;

        for (let i = 0; i < gridCells.length; i++) {
            let value = parseInt(gridCells[i].textContent.trim()) || 0;
            rowData.push(value);
            if ((i + 1) % gridSize === 0) {
                solution.push(rowData);
                rowData = [];
            }
        }

        fetch("/api/submit-solution", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ solution: solution })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("ai-output").textContent = JSON.stringify(data.solution, null, 2);
        })
        .catch(error => console.error("❌ Error submitting solution:", error));
    }

    document.getElementById("load-task-btn").addEventListener("click", loadRandomTask);
    document.getElementById("submit-task-btn").addEventListener("click", submitSolution);

    // ✅ Ensure ARCGrid is globally available
    window.ARCGrid = ARCGrid;
    console.log("✅ ARCGrid is now globally available.");

    // ✅ Auto-load a task when the page loads, but only if elements exist
    if (document.getElementById("test-grid-container") && document.getElementById("output-grid-container")) {
        loadRandomTask();
    } else {
        console.warn("⚠️ Grids not found on page load. Load manually.");
    }
});
