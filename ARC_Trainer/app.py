from flask import Flask, request, jsonify
from loguru import logger
from task_manager import TaskManager
from metrics_dashboard import MetricsDashboard
from user_feedback import UserFeedback

app = Flask(__name__)

# Initialize Modules
@app.route("/tasks", methods=["POST"])
def submit_task():
    """
    API endpoint to submit a task.
    """
    try:
        task_data = request.json

        if not task_data:
            return jsonify({"error": "Task data is required"}), 400

        manager = TaskManager()
        response = manager.submit_task(task_data)
        manager.close()
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error in submit_task endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/tasks/<task_id>", methods=["GET"])
def get_task_status(task_id):
    """
    API endpoint to get the status of a task.
    """
    try:
        manager = TaskManager()
        response = manager.get_task_status(task_id)
        manager.close()
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error in get_task_status endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/metrics/tasks", methods=["GET"])
def get_task_metrics():
    """
    API endpoint to fetch task metrics.
    """
    try:
        metrics = MetricsDashboard().get_task_metrics()
        return jsonify(metrics), 200
    except Exception as e:
        logger.error(f"Error in get_task_metrics endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/metrics/system", methods=["GET"])
def get_system_metrics():
    """
    API endpoint to fetch system performance metrics.
    """
    try:
        metrics = MetricsDashboard().get_system_metrics()
        return jsonify(metrics), 200
    except Exception as e:
        logger.error(f"Error in get_system_metrics endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/feedback", methods=["POST"])
def submit_feedback():
    """
    API endpoint to submit user feedback.
    """
    try:
        data = request.json
        session_id = data.get("session_id")
        feedback = data.get("feedback")

        if not session_id or not feedback:
            return jsonify({"error": "session_id and feedback are required"}), 400

        user_feedback = UserFeedback()
        success = user_feedback.submit_feedback(session_id, feedback)
        user_feedback.close()

        if success:
            return jsonify({"message": "Feedback submitted successfully"}), 200
        else:
            return jsonify({"error": "Failed to store feedback"}), 500
    except Exception as e:
        logger.error(f"Error in submit_feedback endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/feedback/<session_id>", methods=["GET"])
def get_feedback(session_id):
    """
    API endpoint to retrieve user feedback for a session.
    """
    try:
        user_feedback = UserFeedback()
        feedback = user_feedback.get_feedback(session_id)
        user_feedback.close()
        return jsonify({"session_id": session_id, "feedback": feedback}), 200
    except Exception as e:
        logger.error(f"Error in get_feedback endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    logger.info("Starting ARC Trainer API")
    app.run(host="0.0.0.0", port=5000)
