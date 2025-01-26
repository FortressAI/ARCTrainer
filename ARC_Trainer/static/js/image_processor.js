document.addEventListener("DOMContentLoaded", function () {
    initializeEventListeners();
});

// Function to initialize event listeners
function initializeEventListeners() {
    document.getElementById("process-image").addEventListener("click", processImage);
    document.getElementById("load-arc-task").addEventListener("click", loadARCTask);
    document.getElementById("validate-reasoning").addEventListener("click", validateReasoning);
}

// Function to send image to the backend for processing
async function processImage() {
    let imageFile = document.getElementById("image-upload").files[0];

    if (!imageFile) {
        alert("Please upload an image first.");
        return;
    }

    let formData = new FormData();
    formData.append("image", imageFile);

    try {
        let response = await fetch("/api/upload-image", {
            method: "POST",
            body: formData
        });

        let data = await response.json();
        document.getElementById("language-game-output").innerHTML = `
            <p><strong>AI Description:</strong> ${data.image_caption}</p>
            <p><strong>Reasoning Challenge:</strong> ${data.reasoning_prompt}</p>
        `;
    } catch (error) {
        console.error("Error processing image:", error);
        alert("Failed to process image.");
    }
}

// Function to load an ARC dataset task from the backend
async function loadARCTask() {
    let taskName = document.getElementById("arc-task-name").value || "default_task";

    try {
        let response = await fetch(`/api/load-arc-task?task_name=${taskName}`);
        let data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        document.getElementById("arc-task-output").innerText = JSON.stringify(data.task_data, null, 2);
    } catch (error) {
        console.error("Error loading ARC task:", error);
        alert("Failed to load ARC task.");
    }
}

// Function to validate AI-generated reasoning against logic rules
async function validateReasoning() {
    let reasoningInput = document.getElementById("reasoning-input").value.trim();

    if (!reasoningInput) {
        alert("Please enter reasoning input.");
        return;
    }

    try {
        let response = await fetch("/api/validate-reasoning", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ reasoning_input: reasoningInput })
        });

        let data = await response.json();
        let validationStatus = data.is_valid ? "✅ Valid reasoning" : "❌ Invalid reasoning";

        document.getElementById("reasoning-validation-output").innerHTML = `
            <p><strong>Input:</strong> ${data.input}</p>
            <p><strong>Validation:</strong> ${validationStatus}</p>
        `;
    } catch (error) {
        console.error("Error validating reasoning:", error);
        alert("Failed to validate reasoning.");
    }
}
