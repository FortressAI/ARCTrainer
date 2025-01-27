document.addEventListener("DOMContentLoaded", function() {
    class KnowledgeGraph {
        constructor() {
            this.loadKnowledgeGraph();
        }

        loadKnowledgeGraph() {
            API.request("/api/get-knowledge-graph")
            .then(data => {
                this.displayKnowledgeGraph(data);
            })
            .catch(error => {
                Logger.error("Knowledge Graph Error:", error);
                UIHelpers.showAlert("Failed to load Knowledge Graph.", "error");
            });
        }

        displayKnowledgeGraph(kgData) {
            let kgContainer = document.getElementById("kg-visual");
            kgContainer.innerHTML = "";

            kgData.nodes.forEach(node => {
                let nodeElement = document.createElement("div");
                nodeElement.classList.add("kg-node");
                nodeElement.textContent = `Rule: ${node.rule}`;
                nodeElement.dataset.nodeId = node.id;
                
                if (node.validated_by_human) {
                    nodeElement.classList.add("human-validated");
                } else {
                    nodeElement.classList.add("ai-validated");
                }

                let validateButton = document.createElement("button");
                validateButton.textContent = "Validate";
                validateButton.addEventListener("click", () => this.validateKnowledge(node.id));
                nodeElement.appendChild(validateButton);

                let removeButton = document.createElement("button");
                removeButton.textContent = "Remove";
                removeButton.addEventListener("click", () => this.removeKnowledge(node.id));
                nodeElement.appendChild(removeButton);

                kgContainer.appendChild(nodeElement);
            });
        }

        validateKnowledge(nodeId) {
            API.request("/api/validate-knowledge", "POST", { node_id: nodeId })
            .then(data => {
                UIHelpers.showAlert("Knowledge validated: " + data.status, "success");
                this.loadKnowledgeGraph();
            })
            .catch(error => {
                Logger.error("Knowledge Validation Error:", error);
                UIHelpers.showAlert("Validation failed.", "error");
            });
        }

        removeKnowledge(nodeId) {
            API.request("/api/remove-knowledge", "POST", { node_id: nodeId })
            .then(data => {
                UIHelpers.showAlert("Knowledge removed: " + data.status, "success");
                this.loadKnowledgeGraph();
            })
            .catch(error => {
                Logger.error("Knowledge Removal Error:", error);
                UIHelpers.showAlert("Failed to remove knowledge.", "error");
            });
        }
    }

    new KnowledgeGraph();
});