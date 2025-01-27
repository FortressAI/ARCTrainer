document.addEventListener("DOMContentLoaded", function() {
    class ImageProcessor {
        constructor() {
            this.initUploadButton();
        }

        initUploadButton() {
            document.getElementById("upload-image-btn").addEventListener("change", (event) => this.processImage(event));
        }

        processImage(event) {
            let file = event.target.files[0];
            if (!file) return UIHelpers.showAlert("Please select an image file.", "error");

            let formData = new FormData();
            formData.append("image", file);

            API.request("/api/process-image", "POST", formData, true)
            .then(data => {
                document.getElementById("image-output").textContent = JSON.stringify(data, null, 2);
            })
            .catch(error => {
                Logger.error("Image Processing Error:", error);
                UIHelpers.showAlert("Failed to process image.", "error");
            });
        }
    }

    new ImageProcessor();
});
