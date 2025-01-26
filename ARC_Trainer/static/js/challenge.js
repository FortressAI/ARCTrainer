document.getElementById("process-image").addEventListener("click", async function () {
    let imageFile = document.getElementById("image-upload").files[0];
    if (!imageFile) {
        alert("Please upload an image first.");
        return;
    }
    let formData = new FormData();
    formData.append("image", imageFile);
    let response = await fetch("/api/upload-image", { method: "POST", body: formData });
    let data = await response.json();
    document.getElementById("image-reasoning").innerText = data.message;
});

document.getElementById("validate-reasoning").addEventListener("click", async function () {
    let reasoningInput = document.getElementById("reasoning-input").value;
    let response = await fetch("/api/validate-reasoning", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reasoning_input: reasoningInput })
    });
    let data = await response.json();
    document.getElementById("reasoning-output").innerText = data.is_valid ? "Valid" : "Invalid";
});
