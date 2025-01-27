import os
import json
import torch
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from PIL import Image
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

task_manager = TaskManager()

# -------------------- ARC Dataset Processing --------------------
@app.route("/api/load-arc-task", methods=["GET"])
def load_arc_task():
    """Loads an ARC dataset task using TaskManager."""
    task_name = request.args.get("task_name", "default_task")
    response, status_code = task_manager.load_arc_task(task_name)
    return jsonify(response), status_code

@app.route("/api/process-arc-task", methods=["POST"])
def process_arc_task():
    """Handles ARC task processing, AI solving, and human intervention."""
    data = request.json
    task_name = data.get("task_name")
    if not task_name:
        return jsonify({"error": "Missing task_name"}), 400

    task_data, status = task_manager.load_arc_task(task_name)
    if status != 200:
        return jsonify(task_data), status

    solution, success = task_manager.attempt_solution(task_data)
    if not success:
        solution = task_manager.human_intervention(task_data)
    task_manager.log_to_knowledge_graph(task_name, solution, success)
    return jsonify({"task": task_name, "solution": solution, "success": success})

# -------------------- Knowledge Graph Visualization --------------------
@app.route("/api/knowledge-graph", methods=["GET"])
def get_knowledge_graph():
    """Fetches stored AI task reasoning and Prolog rules from the Knowledge Graph."""
    graph_data = task_manager.fetch_knowledge_graph()
    return jsonify(graph_data)

@app.route("/")
def knowledge_graph_page():
    """Renders the main ARC interface with Knowledge Graph visualization."""
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
