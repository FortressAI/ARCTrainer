/* 
 * File: static/js/debate_history.js
 * Purpose: Manages multi-agent debate logs, loads example grids, handles human validation.
 */

document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ debate_history.js loaded.");

    class DebateHistory {
        constructor() {
            // If your HTML has these buttons or elements, we hook them up:
            this.initDebateButton();
            this.loadHumanValidationQueue();

            // If you want to load all examples at start:
            this.loadAllExamples();
        }

        // -------------------------------
        //  1) LOAD ALL EXAMPLES
        // -------------------------------
        async loadAllExamples() {
            try {
                let response = await fetch("/api/load-all-examples");
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                let data = await response.json();
                console.log("✅ Loaded Debate Examples:", data);

                if (!data || !Array.isArray(data)) {
                    console.warn("⚠️ No valid examples found.");
                    return;
                }

                this.displayExamples(data);
            } catch (error) {
                console.error("❌ Error loading examples:", error);
            }
        }

        displayExamples(examples) {
            let container = document.getElementById("debate-examples");
            
            if (!container) {
                console.error("❌ Error: #debate-examples container not found in the DOM.");
                return;
            }

            container.innerHTML = ""; // Clear old content

            examples.forEach((example, index) => {
                let exampleWrapper = document.createElement("div");
                exampleWrapper.classList.add("example-wrapper");

                // Create input image reference
                let inputDiv = document.createElement("div");
                inputDiv.innerHTML = `
                  <div class='example-title'>Input ${index + 1}</div>
                  <img src='/api/generate-png?pair=input&index=${index}&task=${example.task}' alt='Input Grid' />
                `;

                // Create output image reference
                let outputDiv = document.createElement("div");
                outputDiv.innerHTML = `
                  <div class='example-title'>Expected Output</div>
                  <img src='/api/generate-png?pair=output&index=${index}&task=${example.task}' alt='Output Grid' />
                `;

                exampleWrapper.appendChild(inputDiv);
                exampleWrapper.appendChild(outputDiv);
                container.appendChild(exampleWrapper);
            });
        }

        // -------------------------------
        //  2) START DEBATE & LOAD LOGS
        // -------------------------------
        initDebateButton() {
            let btn = document.getElementById("start-debate");
            if (btn) {
                btn.addEventListener("click", () => this.startDebate());
            }
        }

        async startDebate() {
            let response = await fetch("/api/start-ai-debate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ allExamples: true })
            });
            let data = await response.json();
            console.log("Debate started:", data);

            // You might show the result in #debate-log or load logs next
            this.loadDebateLogs();
        }

        loadDebateLogs() {
            // If you have a specific puzzle name, pass it. Otherwise, no param => all logs
            fetch("/api/get-debate-history")
            .then(res => res.json())
            .then(data => {
                console.log("Debate logs received:", data.debate_log);
                let logContainer = document.getElementById("debate-log");
                if (!logContainer) return;

                logContainer.innerHTML = "";
                data.debate_log.forEach(entry => {
                    let p = document.createElement("p");
                    p.textContent = `[${entry.timestamp}] ${entry.text}`;
                    logContainer.appendChild(p);
                });
            })
            .catch(err => console.error("Error loading debate logs:", err));
        }

        // -------------------------------
        //  3) HUMAN VALIDATION QUEUE
        // -------------------------------
        async loadHumanValidationQueue() {
            try {
                let response = await fetch("/api/human-validation-queue");
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                let data = await response.json();
                console.log("✅ Validation queue:", data);

                let queueContainer = document.getElementById("human-validation-queue");
                if (!queueContainer) return;
                
                queueContainer.innerHTML = "";
                data.queue.forEach(task => {
                    let taskEntry = document.createElement("div");
                    taskEntry.classList.add("validation-task");

                    let taskInfo = document.createElement("p");
                    taskInfo.textContent = `Task Data: ${JSON.stringify(task)}`;
                    taskEntry.appendChild(taskInfo);

                    let approveButton = document.createElement("button");
                    approveButton.textContent = "Approve";
                    approveButton.addEventListener("click", () => this.validateHumanDecision(task, "approved"));
                    taskEntry.appendChild(approveButton);

                    let rejectButton = document.createElement("button");
                    rejectButton.textContent = "Reject";
                    rejectButton.addEventListener("click", () => this.validateHumanDecision(task, "rejected"));
                    taskEntry.appendChild(rejectButton);

                    queueContainer.appendChild(taskEntry);
                });
            } catch (error) {
                console.error("Error loading human validation queue:", error);
            }
        }

        async validateHumanDecision(task, decision) {
            try {
                await fetch("/api/validate-reasoning", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ task: task, decision: decision })
                });
                alert("Decision recorded: " + decision);
                this.loadHumanValidationQueue();
            } catch (error) {
                console.error("Error validating reasoning:", error);
            }
        }
    }

    // Initialize everything
    new DebateHistory();
});
