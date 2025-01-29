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

        renderGrid(data, editable = false) {
            if (!this.gridContainer) return;
            this.gridContainer.innerHTML = "";
            if (!data || data.length === 0) {
                console.error("❌ Attempted to render an empty grid.");
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
                    div.textContent = "";
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
            let validValues = ["0", "1", "2", "3", "4", "5", "6", "7", "8"];
            let newValue = cell.textContent.trim();
            if (!validValues.includes(newValue)) {
                cell.textContent = "";
            } else {
                let row = parseInt(cell.dataset.row);
                let col = parseInt(cell.dataset.col);
                this.gridData[row][col] = newValue;
                cell.style.backgroundColor = getColorForValue(newValue);
                cell.textContent = "";
            }
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

    const trainContainer = document.getElementById("train-examples");
    
    document.getElementById("load-task-btn").addEventListener("click", function() {
        let fileInput = document.getElementById("load-task-file");
        let file = fileInput.files[0];
        if (!file) return alert("Please select a task file.");

        let reader = new FileReader();
        reader.onload = function(e) {
            let taskData = JSON.parse(e.target.result);
            console.log("📥 Loaded Task Data:", taskData);
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
                
                new GridRenderer(`input-grid-${index}`).renderGrid(example.input);
                new GridRenderer(`output-grid-${index}`).renderGrid(example.output);
            });
            
            let testGrid = new GridRenderer("test-grid-container");
            testGrid.renderGrid(taskData.test[0].input, true);
        };
        reader.readAsText(file);
    });
});