import os
import json
import time
from flask import Flask, request, jsonify, render_template, send_file
from dotenv import load_dotenv
from PIL import Image

# Import your modules
from src.task_manager import TaskManager
from src.graph_rag import GraphRAG

# Load environment variables (DB credentials, BLIP tokens, etc.)
load_dotenv()

app = Flask(__name__, template_folder="templates")

# Instantiate manager objects
task_manager = TaskManager()
graph_rag = GraphRAG()

@app.route("/")
def index():
    """Landing page that offers ARC mode or LHE mode."""
    return render_template("index.html")

@app.route("/arc")
def arc_page():
    """Renders the main ARC mode page (arc.html)."""
    return render_template("arc.html")

@app.route("/lhe")
def lhe_page():
    """Renders the Last Human Exam mode page (lhe.html)."""
    return render_template("lhe.html")

# Knowledge Graph pages for ARC or LHE
@app.route("/arc/knowledge-graph")
def arc_knowledge_graph_page():
    return render_template("arc_knowledge_graph.html")

@app.route("/lhe/knowledge-graph")
def lhe_knowledge_graph_page():
    return render_template("lhe_knowledge_graph.html")

# ------------------------------------------------------------------
#    ARC TASK ENDPOINTS
# ------------------------------------------------------------------

@app.route("/api/load-random-arc-task", methods=["GET"])
def load_random_arc_task():
    """
    Calls the advanced pipeline in TaskManager:
      - Picks a random puzzle
      - Generates images, calls BLIP for training & test input
      - Asks LLM for solution
      - Compares guess vs. correct solution
      - Logs success/fail in KG
      - Returns puzzle data + guess + success/fail + real solution
    """
    response, status_code = task_manager.get_random_task()
    return jsonify(response), status_code

@app.route("/api/load-arc-task", methods=["GET"])
def load_arc_task():
    """
    Simpler approach: loads puzzle data from JSON, optionally revealing solution.
    """
    task_name = request.args.get("task_name", "default_task")
    reveal = request.args.get("reveal", "false").lower() == "true"

    response, status_code = task_manager.load_arc_task(task_name, reveal_solution=reveal)
    return jsonify(response), status_code

@app.route("/api/process-arc-task", methods=["POST"])
def process_arc_task():
    """
    Older approach: user-submitted solution, do minimal LLM logic, store result.
    """
    data = request.json
    task_name = data.get("task_name", "unknown_task")
    user_solution = data.get("solution", [])

    loaded_data, status = task_manager.load_arc_task(task_name, reveal_solution=True)
    if status != 200:
        return jsonify(loaded_data), status

    solution, success = task_manager.attempt_solution(loaded_data, user_solution)
    return jsonify({"task": task_name, "solution": solution, "success": success})

# ------------------------------------------------------------------
#    LHE TASK ENDPOINTS (Placeholders or partial logic)
# ------------------------------------------------------------------

@app.route("/api/load-lhe-task", methods=["GET"])
def load_lhe_task():
    """
    Placeholder for LHE mode. 
    """
    response, status_code = task_manager.load_lhe_task("default_lhe")
    return jsonify(response), status_code

@app.route("/api/process-lhe-task", methods=["POST"])
def process_lhe_task():
    """
    Placeholder for LHE mode logic.
    """
    data = request.json
    task_name = data.get("task_name", "default_lhe")
    response, status_code = task_manager.load_lhe_task(task_name)
    return jsonify(response), status_code

# ------------------------------------------------------------------
#    MULTI-AGENT DEBATE ENDPOINTS
# ------------------------------------------------------------------

@app.route("/api/get-debate-history", methods=["GET"])
def get_debate_history():
    """
    Fetch logs from knowledge graph. If ?task_name=somePuzzle is given, 
    we filter logs for that puzzle; else returns all logs.
    """
    task_name = request.args.get("task_name")  # e.g. "default_task"
    logs = graph_rag.fetch_debate_history(task_name)
    return jsonify({"debate_log": logs}), 200

@app.route("/api/start-ai-debate", methods=["POST"])
def start_ai_debate():
    """
    Example route to store new debate messages. 
    In a real scenario, you'd orchestrate actual multi-agent logic.
    Here we store sample messages for demonstration.
    """
    data = request.json or {}
    task_name = data.get("task_name", "default_task")

    now = int(time.time())
    graph_rag.store_debate_message(task_name, "Agent1: I propose a color-based approach.", now)

    now2 = int(time.time())
    graph_rag.store_debate_message(task_name, "Agent2: Alternatively, shape-based strategy might work better.", now2)

    return jsonify({"status": "debate started", "task_name": task_name}), 200

# ------------------------------------------------------------------
#    HUMAN VALIDATION & EXAMPLES
# ------------------------------------------------------------------

@app.route("/api/load-all-examples", methods=["GET"])
def load_all_examples():
    """
    Used by debate_history.js to show example puzzle images 
    if you want a list of tasks or pairs to display.
    Returns an array of { "task": "...", ... } objects.
    """
    from pathlib import Path
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATASET_DIR = Path(BASE_DIR) / "datasets/evaluation"

    # Gather .json puzzle files as "examples"
    puzzle_files = [f.stem for f in DATASET_DIR.glob("*.json")]
    data = []
    for puzzle_name in puzzle_files:
        data.append({"task": puzzle_name})

    return jsonify(data), 200

@app.route("/api/human-validation-queue", methods=["GET"])
def get_human_validation_queue():
    """
    Returns a placeholder queue for user validation tasks.
    In a real system, you'd query KG or a queue table for pending tasks.
    """
    queue = [
        {"task_name": "someTask1", "status": "pending"},
        {"task_name": "someTask2", "status": "pending"}
    ]
    return jsonify({"queue": queue}), 200

@app.route("/api/validate-reasoning", methods=["POST"])
def validate_reasoning():
    """
    Called by the front-end when user approves/rejects a solution or reasoning.
    The request body includes { task: ..., decision: ... }.
    Here we do a simple placeholder storing or logging that decision.
    """
    data = request.json or {}
    task = data.get("task")
    decision = data.get("decision")

    # In a real system, you'd store this feedback in KG or a separate table
    print(f"User validated reasoning for task {task} with decision={decision}")

    return jsonify({"status": "Decision recorded", "task": task, "decision": decision}), 200

# ------------------------------------------------------------------
#    UTILITY: GENERATE-PNG ENDPOINT
# ------------------------------------------------------------------

@app.route("/api/generate-png", methods=["GET"])
def generate_png_route():
    """
    Example route for retrieving a PNG of an input/output grid by filename 
    if your code previously saved these images in 'generated_images/'.
    Expects query params: ?task=..., pair=input|output, index=int
    """
    from pathlib import Path
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    IMAGE_DIR = Path(BASE_DIR) / "generated_images"

    task_name = request.args.get("task", "unknown")
    pair_type = request.args.get("pair", "input")
    index = request.args.get("index", "0")

    filename = f"{task_name}_{pair_type}_{index}.png"
    filepath = IMAGE_DIR / filename

    if not filepath.exists():
        return jsonify({"error": "PNG not found"}), 404

    return send_file(filepath, mimetype="image/png")

# ------------------------------------------------------------------
#    FLASK MAIN
# ------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
