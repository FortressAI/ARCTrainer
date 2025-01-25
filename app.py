from flask import Flask, request, jsonify
import os
import json
import torch
import requests
from dotenv import load_dotenv
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

# Load environment variables from .env file
load_dotenv()

# Get Hugging Face API credentials from environment variables
HF_BLIP_ENDPOINT = os.getenv("HF_BLIP_ENDPOINT")
HF_BEARER_TOKEN = os.getenv("HF_BEARER_TOKEN")

USE_HF_API = bool(HF_BLIP_ENDPOINT and HF_BEARER_TOKEN)

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
DATASET_FOLDER = "datasets"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATASET_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Initialize Local BLIP Model (Only if Hugging Face API is not used)
if not USE_HF_API:
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

# -------------------- ARC Dataset Processing --------------------

def load_arc_task(task_name):
    """Loads an ARC dataset task from the datasets folder."""
    task_file = os.path.join(DATASET_FOLDER, "evaluation", f"{task_name}.json")
    
    if not os.path.exists(task_file):
        return None

    with open(task_file, "r") as f:
        return json.load(f)

@app.route("/api/load-arc-task", methods=["GET"])
def load_arc_test():
    """Loads an ARC dataset task for AI processing."""
    task_name = request.args.get("task_name", "default_task")  # Default ARC task

    task = load_arc_task(task_name)
    if task is None:
        return jsonify({"error": f"Task '{task_name}' not found."}), 404

    return jsonify({"task_name": task_name, "task_data": task})

# -------------------- Image Processing (Last Human Test) --------------------

def process_image_with_huggingface(image_path):
    """Sends image to Hugging Face API for caption generation."""
    with open(image_path, "rb") as img_file:
        headers = {"Authorization": f"Bearer {HF_BEARER_TOKEN}"}
        response = requests.post(HF_BLIP_ENDPOINT, headers=headers, files={"image": img_file})

    if response.status_code == 200:
        return response.json().get("generated_text", "No caption generated.")
    else:
        return f"Error: {response.status_code}, {response.text}"

def process_image_locally(image_path):
    """Processes image using local BLIP model."""
    raw_image = Image.open(image_path).convert("RGB")
    inputs = processor(raw_image, return_tensors="pt")
    generated_ids = model.generate(**inputs)
    return processor.decode(generated_ids[0], skip_special_tokens=True)

@app.route("/api/upload-image", methods=["POST"])
def upload_image():
    """Handles image uploads, processes them with BLIP, and generates reasoning challenges."""
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]
    file_path = os.path.normpath(os.path.join(app.config["UPLOAD_FOLDER"], image.filename))
    if not file_path.startswith(os.path.abspath(app.config["UPLOAD_FOLDER"])):
        return jsonify({"error": "Invalid file path"}), 400
    image.save(file_path)

    # Process image with Hugging Face API or local model
    if USE_HF_API:
        caption = process_image_with_huggingface(file_path)
    else:
        caption = process_image_locally(file_path)

    # Generate a reasoning challenge based on the image description
    reasoning_prompt = f"Based on the image description '{caption}', generate a logical puzzle."

    return jsonify({"image_caption": caption, "reasoning_prompt": reasoning_prompt})

# -------------------- AI Reasoning & Validation --------------------

@app.route("/api/validate-reasoning", methods=["POST"])
def validate_reasoning():
    """Validates AI-generated reasoning against structured logic rules."""
    data = request.json
    reasoning_input = data.get("reasoning_input", "")

    if not reasoning_input:
        return jsonify({"error": "No reasoning input provided."}), 400

    # Placeholder logic validation (Replace with Prolog or symbolic logic validation)
    is_valid = "error" not in reasoning_input.lower()  # Simple rule for demonstration

    return jsonify({"input": reasoning_input, "is_valid": is_valid})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
