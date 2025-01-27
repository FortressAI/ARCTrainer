document.addEventListener("DOMContentLoaded", function () {
    class DebateHistory {
        constructor() {
            this.loadDebateHistory();
            this.loadHumanValidationQueue();
            this.initDebateButton();
        }

        initDebateButton() {
            document.getElementById("start-debate").addEventListener("click", async () => {
                let debateRule = document.getElementById("debate-rule").value;
                let response = await fetch("/api/debate", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ rule: debateRule })
                });
                let data = await response.json();
                this.displayDebateResults(data);
                this.loadDebateHistory();
                this.loadHumanValidationQueue();
            });
        }

        loadDebateHistory() {
            fetch("/api/get-debate-history")
                .then(response => response.json())
                .then(data => {
                    this.displayDebateHistory(data.debate_log);
                })
                .catch(error => console.error("Error loading debate history:", error));
        }

        loadHumanValidationQueue() {
            fetch("/api/human-validation-queue")
                .then(response => response.json())
                .then(data => {
                    this.displayHumanValidationQueue(data.queue);
                })
                .catch(error => console.error("Error loading human validation queue:", error));
        }

        displayDebateResults(data) {
            document.getElementById("agent1-response").innerText = `Agent 1: ${data.agent1}`;
            document.getElementById("agent2-response").innerText = `Agent 2: ${data.agent2}`;
            document.getElementById("judge-decision").innerText = `Judge Decision: ${data.judge}`;
            document.getElementById("contradiction-result").innerText = data.contradiction_found ? "Yes" : "No";
        }

        displayDebateHistory(debateLog) {
            let debateContainer = document.getElementById("debate-log");
            debateContainer.innerHTML = "";
            debateLog.forEach(debate => {
                let debateEntry = document.createElement("div");
                debateEntry.classList.add("debate-entry");
                
                let rule = document.createElement("p");
                rule.textContent = `Rule: ${debate.rule}`;
                debateEntry.appendChild(rule);
                
                let agents = document.createElement("p");
                agents.textContent = `Agent 1: ${debate.agent1}, Agent 2: ${debate.agent2}`;
                debateEntry.appendChild(agents);
                
                let judge = document.createElement("p");
                judge.textContent = `Judge Decision: ${debate.judge}`;
                debateEntry.appendChild(judge);
                
                let contradiction = document.createElement("p");
                contradiction.textContent = debate.contradiction ? "⚠ Contradiction Detected" : "✓ No Contradiction";
                contradiction.classList.add(debate.contradiction ? "contradiction-highlight" : "valid-highlight");
                debateEntry.appendChild(contradiction);

                debateContainer.appendChild(debateEntry);
            });
        }

        displayHumanValidationQueue(queue) {
            let queueContainer = document.getElementById("human-validation-queue");
            queueContainer.innerHTML = "";
            queue.forEach(task => {
                let taskEntry = document.createElement("div");
                taskEntry.classList.add("validation-task");
                
                let taskInfo = document.createElement("p");
                taskInfo.textContent = `Task Data: ${JSON.stringify(task.task)}`;
                taskEntry.appendChild(taskInfo);
                
                let debateInfo = document.createElement("p");
                debateInfo.textContent = `Debate Arguments: ${JSON.stringify(task.debate)}`;
                taskEntry.appendChild(debateInfo);
                
                let approveButton = document.createElement("button");
                approveButton.textContent = "Approve";
                approveButton.addEventListener("click", () => this.validateHumanDecision(task.task, "approved"));
                taskEntry.appendChild(approveButton);

                let rejectButton = document.createElement("button");
                rejectButton.textContent = "Reject";
                rejectButton.addEventListener("click", () => this.validateHumanDecision(task.task, "rejected"));
                taskEntry.appendChild(rejectButton);

                queueContainer.appendChild(taskEntry);
            });
        }

        validateHumanDecision(task, decision) {
            fetch("/api/validate-reasoning", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ task: task, decision: decision })
            })
            .then(response => response.json())
            .then(data => {
                alert(`Decision recorded: ${decision}`);
                this.loadHumanValidationQueue();
            })
            .catch(error => console.error("Error validating decision:", error));
        }
    }

    new DebateHistory();
});