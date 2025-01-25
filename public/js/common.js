// js/common.js

// Utility function to make API requests
async function apiRequest(url, method = "GET", body = null) {
    try {
        const options = {
            method,
            headers: {
                "Content-Type": "application/json",
            },
        };

        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(url, options);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Unknown error occurred");
        }

        return result;
    } catch (error) {
        console.error(`API Request Error: ${error.message}`);
        throw error;
    }
}

// Function to display messages in the UI
function displayMessage(message, type = "info") {
    const messageBox = document.getElementById("message-box");
    if (messageBox) {
        messageBox.textContent = message;
        messageBox.className = type; // Apply class for styling (e.g., info, success, error)
    }
}

// Function to handle grid updates
function updateGrid(gridData) {
    const gridContainer = document.getElementById("grid-container");
    if (gridContainer) {
        gridContainer.innerHTML = ""; // Clear the grid

        gridData.forEach((row) => {
            const rowElement = document.createElement("div");
            rowElement.className = "grid-row";

            row.forEach((cell) => {
                const cellElement = document.createElement("div");
                cellElement.className = `grid-cell cell-${cell}`;
                rowElement.appendChild(cellElement);
            });

            gridContainer.appendChild(rowElement);
        });
    }
}

// Function to reset the grid
function resetGrid() {
    const gridContainer = document.getElementById("grid-container");
    if (gridContainer) {
        gridContainer.innerHTML = ""; // Clear the grid
    }
}

// Function to handle feedback submission
async function submitFeedback(sessionId, feedbackText) {
    try {
        const result = await apiRequest("/feedback", "POST", {
            session_id: sessionId,
            feedback: feedbackText,
        });

        displayMessage("Feedback submitted successfully!", "success");
    } catch (error) {
        displayMessage(`Failed to submit feedback: ${error.message}`, "error");
    }
}

// Function to fetch metrics
async function fetchMetrics(metricType) {
    try {
        const url = metricType === "tasks" ? "/metrics/tasks" : "/metrics/system";
        const metrics = await apiRequest(url);

        console.log(`Fetched ${metricType} metrics:`, metrics);
        displayMessage(`Metrics fetched successfully! Check console for details.`, "success");
    } catch (error) {
        displayMessage(`Failed to fetch metrics: ${error.message}`, "error");
    }
}

// Function to initialize event listeners
function initializeEventListeners() {
    const resetButton = document.getElementById("reset-grid");
    if (resetButton) {
        resetButton.addEventListener("click", resetGrid);
    }

    const feedbackButton = document.getElementById("submit-feedback");
    if (feedbackButton) {
        feedbackButton.addEventListener("click", () => {
            const sessionId = document.getElementById("session-id").value;
            const feedbackText = document.getElementById("feedback-text").value;
            submitFeedback(sessionId, feedbackText);
        });
    }

    const fetchMetricsButton = document.getElementById("fetch-metrics");
    if (fetchMetricsButton) {
        fetchMetricsButton.addEventListener("click", () => {
            const metricType = document.getElementById("metric-type").value;
            fetchMetrics(metricType);
        });
    }
}

// Initialize event listeners on page load
document.addEventListener("DOMContentLoaded", initializeEventListeners);
