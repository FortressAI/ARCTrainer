from flask import Flask, request, jsonify
import os
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

app = Flask(__name__)

# Initialize BLIP model
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/api/upload-image", methods=["POST"])
def upload_image():
    """Processes uploaded image, generates a description, and creates a reasoning challenge."""
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
    image.save(file_path)

    # Process Image with BLIP
    raw_image = Image.open(file_path).convert("RGB")
    inputs = processor(raw_image, return_tensors="pt")
    generated_ids = model.generate(**inputs)
    caption = processor.decode(generated_ids[0], skip_special_tokens=True)

    # Generate Reasoning Challenge
    reasoning_prompt = f"Based on the image description '{caption}', generate a logical puzzle."
    
    return jsonify({"image_caption": caption, "reasoning_prompt": reasoning_prompt})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
