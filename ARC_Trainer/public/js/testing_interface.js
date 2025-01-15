// js/testing_interface.js

// Function to handle task submission
document.getElementById("submit-task").addEventListener("click", async () => {
    const gridData = getGridData(); // Function to retrieve current grid data from UI

    try {
        const response = await fetch("/tasks", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ task_data: gridData }),
        });

        const result = await response.json();

        if (response.ok) {
            displayMessage(`Task submitted! Task ID: ${result.task_id}`);
            pollTaskStatus(result.task_id); // Start polling for task status
        } else {
            displayMessage(`Error submitting task: ${result.error}`);
        }
    } catch (error) {
        displayMessage(`An error occurred: ${error.message}`);
    }
});

// Function to poll task status
async function pollTaskStatus(taskId) {
    const intervalId = setInterval(async () => {
        try {
            const response = await fetch(`/tasks/${taskId}`);
            const result = await response.json();

            if (result.status === "completed") {
                displayMessage("Task completed!", "success");
                displayGridResult(result.result); // Update grid with the result
                clearInterval(intervalId);
            } else if (result.status === "failed") {
                displayMessage("Task failed: " + result.error, "error");
                clearInterval(intervalId);
            }
        } catch (error) {
            displayMessage(`Error fetching task status: ${error.message}`, "error");
            clearInterval(intervalId);
        }
    }, 2000); // Poll every 2 seconds
}

// Function to submit feedback
document.getElementById("submit-feedback").addEventListener("click", async () => {
    const sessionId = getSessionId(); // Retrieve session ID from the UI
    const feedback = getFeedbackText(); // Retrieve feedback text from the UI

    try {
        const response = await fetch("/feedback", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                session_id: sessionId,
                feedback: feedback,
            }),
        });

        const result = await response.json();

        if (response.ok) {
            displayMessage("Feedback submitted successfully!", "success");
        } else {
            displayMessage(`Error submitting feedback: ${result.error}`, "error");
        }
    } catch (error) {
        displayMessage(`An error occurred: ${error.message}`, "error");
    }
});

// Utility functions
function displayMessage(message, type = "info") {
    const messageElement = document.getElementById("message-box");
    messageElement.textContent = message;
    messageElement.className = type; // Set class for styling based on type
}

function displayGridResult(result) {
    // Function to update the grid UI with the task result
    console.log("Displaying grid result:", result);
}

function getGridData() {
    // Function to retrieve current grid data from the UI
    return { grid: [[0, 1, 2], [2, 1, 0], [1, 0, 2]] }; // Placeholder
}

function getSessionId() {
    // Function to retrieve the session ID from the UI
    return "session-12345"; // Placeholder
}

function getFeedbackText() {
    // Function to retrieve feedback text from the UI
    return document.getElementById("feedback-text").value;
}
