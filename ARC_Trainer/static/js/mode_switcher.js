document.addEventListener("DOMContentLoaded", function() {
    class ModeSwitcher {
        constructor() {
            this.currentMode = "arc";
            this.initModeButtons();
        }

        initModeButtons() {
            document.getElementById("arc-mode-btn").addEventListener("click", () => this.switchMode("arc"));
            document.getElementById("debate-mode-btn").addEventListener("click", () => this.switchMode("debate"));
            document.getElementById("kg-mode-btn").addEventListener("click", () => this.switchMode("knowledge_graph"));
        }

        switchMode(mode) {
            this.currentMode = mode;
            document.querySelectorAll(".mode-section").forEach(section => section.style.display = "none");
            document.getElementById(`${mode}-section`).style.display = "block";
        }
    }

    new ModeSwitcher();
});
