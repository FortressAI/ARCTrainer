import os
import json
import torch
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from src.task_manager import TaskManager  # Import centralized ARC dataset handling
from src.graph_rag import GraphRAG  # AI-to-AI debate system

# Load environment variables from .env file
load_dotenv()

# Get Hugging Face API credentials from environment variables
HF_BLIP_ENDPOINT = os.getenv("HF_BLIP_ENDPOINT")
HF_BEARER_TOKEN = os.getenv("HF_BEARER_TOKEN")
USE_HF_API = bool(HF_BLIP_ENDPOINT and HF_BEARER_TOKEN)

app = Flask(__name__, template_folder="templates")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Initialize Local BLIP Model (Only if Hugging Face API is not used)
if not USE_HF_API:
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

# -------------------- ARC Dataset Processing (Delegated to TaskManager) --------------------
@app.route("/api/load-arc-task", methods=["GET"])
def load_arc_test():
    """Loads an ARC dataset task using TaskManager."""
    task_name = request.args.get("task_name", "default_task")
    task_manager = TaskManager()
    response, status_code = task_manager.load_arc_task(task_name)
    task_manager.close()
    return jsonify(response), status_code

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
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
    image.save(file_path)

    # Process image with Hugging Face API or local model
    caption = process_image_with_huggingface(file_path) if USE_HF_API else process_image_locally(file_path)
    reasoning_prompt = f"Based on the image description '{caption}', generate a logical puzzle."

    return jsonify({"image_caption": caption, "reasoning_prompt": reasoning_prompt})

@app.route("/api/render-last-human-exam", methods=["GET"])
def render_last_human_exam():
    """Renders the last human exam results as an HTML page."""
    return render_template("last_human_exam.html")

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

# -------------------- ARC Task Processing --------------------
@app.route("/api/process-arc-task", methods=["POST"])
def process_arc_task():
    """Handles ARC task processing, AI solving, and human intervention."""
    data = request.json
    task_name = data.get("task_name")
    
    if not task_name:
        return jsonify({"error": "Missing task_name"}), 400

    task_manager = TaskManager()
    task_data, status = task_manager.load_arc_task(task_name)
    if status != 200:
        return jsonify(task_data), status

    solution, success = task_manager.attempt_solution(task_data)
    if not success:
        solution = task_manager.human_intervention(task_data)
    task_manager.log_to_knowledge_graph(task_name, solution, success)
    task_manager.close()
    
    return jsonify({"task": task_name, "solution": solution, "success": success})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
