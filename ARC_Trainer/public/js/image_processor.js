document.getElementById("process-image").addEventListener("click", function () {
    let imageFile = document.getElementById("image-upload").files[0];

    if (!imageFile) {
        alert("Please upload an image first.");
        return;
    }

    let formData = new FormData();
    formData.append("image", imageFile);

    fetch("/api/upload-image", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        let caption = data.image_caption;
        let reasoningPrompt = data.reasoning_prompt;

        document.getElementById("language-game-output").innerHTML = `
            <p><strong>AI Description:</strong> ${caption}</p>
            <p><strong>Reasoning Challenge:</strong> ${reasoningPrompt}</p>
        `;
    })
    .catch(error => console.error("Error processing image:", error));
});
