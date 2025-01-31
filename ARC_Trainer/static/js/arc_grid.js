document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ arc_grid.js is loaded.");

    class ARCGrid {
        constructor(gridContainerId, editable = false) {
            this.gridContainer = document.getElementById(gridContainerId);
            this.gridData = [];
            this.editable = editable;
            this.activeSymbol = "0";
            if (!this.gridContainer) {
                console.error(`❌ Error: Grid container '${gridContainerId}' not found.`);
            } else {
                this.initSymbolPicker();
            }
        }

        renderGrid(data) {
            if (!this.gridContainer) return;
            this.gridContainer.innerHTML = "";
            this.gridContainer.style.display = "grid";
            if (!data || !data.length) {
                console.warn("⚠️ Attempted to render an empty or invalid grid.");
                return;
            }

            const rows = data.length;
            const cols = data[0].length;
            this.gridContainer.style.gridTemplateColumns = `repeat(${cols}, 30px)`;
            this.gridContainer.style.gap = "2px";
            this.gridData = data;

            data.forEach((row, rowIndex) => {
                row.forEach((cell, colIndex) => {
                    let div = document.createElement("div");
                    div.classList.add("grid-cell");
                    div.style.backgroundColor = getColorForValue(cell);
                    div.dataset.row = rowIndex;
                    div.dataset.col = colIndex;
                    div.textContent = this.editable ? "" : cell;
                    if (this.editable) {
                        div.contentEditable = "true";
                        div.addEventListener("click", () => {
                            div.textContent = this.activeSymbol;
                            div.style.backgroundColor = getColorForValue(this.activeSymbol);
                        });
                    }
                    this.gridContainer.appendChild(div);
                });
            });
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

    // If you have a loadRandomTask in this file, keep it or remove it if you're using testing_interface.js
    // ...

    window.ARCGrid = ARCGrid;  // Expose globally
});
