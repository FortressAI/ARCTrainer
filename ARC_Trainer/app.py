import os
import json
import torch
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from PIL import Image
from src.task_manager import TaskManager  # Handles ARC & LHE dataset tasks
from src.graph_rag import GraphRAG  # AI-to-AI debate system

# Load environment variables
load_dotenv()

# Get Hugging Face API credentials
HF_BLIP_ENDPOINT = os.getenv("HF_BLIP_ENDPOINT")
HF_BEARER_TOKEN = os.getenv("HF_BEARER_TOKEN")
USE_HF_API = bool(HF_BLIP_ENDPOINT and HF_BEARER_TOKEN)

# Flask App Setup
app = Flask(__name__, template_folder="templates")
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Task Manager Instance
task_manager = TaskManager()

# -------------------- ✅ MAIN PAGE ROUTES --------------------

@app.route("/")
def index():
    """Loads the selection page for ARC or LHE."""
    return render_template("index.html")  # ✅ Now correctly loads index.html

@app.route("/arc")
def arc_page():
    """Loads the ARC Dataset Mode page."""
    return render_template("arc.html")  # ✅ ARC mode now loads arc.html

@app.route("/lhe")
def lhe_page():
    """Loads the LHE Dataset Mode page."""
    return render_template("lhe.html")  # ✅ LHE mode now loads lhe.html

# -------------------- ✅ KNOWLEDGE GRAPH ROUTES --------------------

@app.route("/arc/knowledge-graph")
def arc_knowledge_graph_page():
    """Loads the ARC-specific Knowledge Graph visualization."""
    return render_template("arc_knowledge_graph.html")

@app.route("/lhe/knowledge-graph")
def lhe_knowledge_graph_page():
    """Loads the LHE-specific Knowledge Graph visualization."""
    return render_template("lhe_knowledge_graph.html")

# -------------------- ✅ ARC TASK PROCESSING --------------------

@app.route("/api/load-random-arc-task", methods=["GET"])
def load_random_arc_task():
    """Loads a random ARC dataset task."""
    task_name = task_manager.get_random_task()
    if not task_name:
        return jsonify({"error": "No available tasks"}), 404
    response, status_code = task_manager.load_arc_task(task_name)
    return jsonify(response), status_code

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

# -------------------- ✅ LHE TASK PROCESSING --------------------

@app.route("/api/load-lhe-task", methods=["GET"])
def load_lhe_task():
    """Loads an LHE dataset task using TaskManager."""
    task_name = request.args.get("task_name", "default_task")
    response, status_code = task_manager.load_lhe_task(task_name)
    return jsonify(response), status_code

@app.route("/api/process-lhe-task", methods=["POST"])
def process_lhe_task():
    """Handles LHE task processing, AI solving, and human intervention."""
    data = request.json
    task_name = data.get("task_name")
    if not task_name:
        return jsonify({"error": "Missing task_name"}), 400

    task_data, status = task_manager.load_lhe_task(task_name)
    if status != 200:
        return jsonify(task_data), status

    solution, success = task_manager.attempt_solution(task_data)
    if not success:
        solution = task_manager.human_intervention(task_data)
    task_manager.log_to_knowledge_graph(task_name, solution, success)
    return jsonify({"task": task_name, "solution": solution, "success": success})

# -------------------- ✅ START FLASK SERVER --------------------

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
