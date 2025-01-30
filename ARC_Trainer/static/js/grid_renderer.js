document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ grid_renderer.js is loaded.");

    class GridRenderer {
        constructor(containerId) {
            this.gridContainer = document.getElementById(containerId);
            if (!this.gridContainer) {
                console.error(`❌ Error: Grid container with ID '${containerId}' not found.`);
                return;
            }
            this.gridData = [];
        }

        renderGrid(data, editable = false) {
            if (!this.gridContainer) return;

            this.gridContainer.innerHTML = "";
            if (!data || !Array.isArray(data) || data.length === 0) {
                console.warn("⚠️ Attempted to render an empty or invalid grid.");
                this.gridContainer.innerHTML = "<p class='grid-error'>No data available</p>";
                return;
            }

            const rows = data.length;
            const cols = Math.max(...data.map(row => row.length));
            console.log(`📊 Rendering grid: ${rows} x ${cols}`);

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
                    div.textContent = cell;

                    if (editable) {
                        div.contentEditable = "true";
                        div.addEventListener("input", (event) => this.validateGridInput(event));
                    }
                    this.gridContainer.appendChild(div);
                });
            });
        }

        validateGridInput(event) {
            let cell = event.target;
            let validValues = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];
            let newValue = cell.textContent.trim();

            if (!validValues.includes(newValue)) {
                cell.textContent = "0";
            } else {
                let row = parseInt(cell.dataset.row);
                let col = parseInt(cell.dataset.col);
                this.gridData[row][col] = parseInt(newValue);
                cell.style.backgroundColor = getColorForValue(newValue);
            }
        }

        getGridData() {
            return this.gridData;
        }
    }

    function getColorForValue(value) {
        const colors = {
            "0": "#ffffff", "1": "#000000", "2": "#ff0000", "3": "#00ff00",
            "4": "#0000ff", "5": "#ffff00", "6": "#ff00ff", "7": "#00ffff",
            "8": "#808080", "9": "#a52a2a"
        };
        return colors[value] || "#ffffff";
    }

    function loadTrainingExamples(taskData) {
        let trainContainer = document.getElementById("train-examples");
        trainContainer.innerHTML = "";

        if (!taskData || !taskData.train) {
            console.warn("⚠️ No training examples found.");
            return;
        }

        taskData.train.forEach((example, index) => {
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

            new GridRenderer(`input-grid-${index}`).renderGrid(example.input);
            new GridRenderer(`output-grid-${index}`).renderGrid(example.output);
        });
    }

    function loadTestExample(taskData) {
        let testGridContainer = document.getElementById("test-grid-container");

        if (!taskData || !taskData.test || taskData.test.length === 0) {
            console.warn("⚠️ No test data found in task file.");
            return;
        }

        let testGrid = new GridRenderer("test-grid-container");
        testGrid.renderGrid(taskData.test[0].input, true);
    }

    document.getElementById("load-task-btn").addEventListener("click", function () {
        let fileInput = document.getElementById("load-task-file");
        let file = fileInput?.files?.[0];

        if (!file) {
            alert("⚠️ Please select a task file.");
            return;
        }

        let reader = new FileReader();
        reader.onload = function (e) {
            let taskData = JSON.parse(e.target.result);
            console.log("📥 Loaded Task Data:", taskData);
            loadTrainingExamples(taskData);
            loadTestExample(taskData);
        };

        reader.readAsText(file);
    });

    window.GridRenderer = GridRenderer;
});