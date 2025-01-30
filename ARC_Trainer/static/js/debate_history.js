document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ DOM fully loaded, initializing DebateHistory...");

    class DebateHistory {
        constructor() {
            this.loadAllExamples();
            this.initDebateButton();
            this.loadHumanValidationQueue();
        }

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
                console.error("❌ Error: debate-examples container not found in the DOM.");
                return;
            }
        
            container.innerHTML = "";  // Reset container before adding new examples
        
            examples.forEach((example, index) => {
                let exampleWrapper = document.createElement("div");
                exampleWrapper.classList.add("example-wrapper");
        
                let inputContainer = document.createElement("div");
                inputContainer.innerHTML = `<div class='example-title'>Input ${index + 1}</div><img src='/api/generate-png?pair=input&index=${index}&task=${example.task}' alt='Input Grid' />`;
                
                let outputContainer = document.createElement("div");
                outputContainer.innerHTML = `<div class='example-title'>Expected Output</div><img src='/api/generate-png?pair=output&index=${index}&task=${example.task}' alt='Output Grid' />`;
        
                exampleWrapper.appendChild(inputContainer);
                exampleWrapper.appendChild(outputContainer);
                container.appendChild(exampleWrapper);
            });
        }
        
        async startDebate() {
            let response = await fetch("/api/start-ai-debate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ allExamples: true })
            });
            let data = await response.json();
            document.getElementById("debate-log").textContent = JSON.stringify(data, null, 2);
        }

        initDebateButton() {
            document.getElementById("start-debate").addEventListener("click", () => this.startDebate());
        }

        async loadHumanValidationQueue() {
            try {
                let response = await fetch("/api/human-validation-queue");
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                let data = await response.json();
                let queueContainer = document.getElementById("human-validation-queue");
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

    new DebateHistory();
});