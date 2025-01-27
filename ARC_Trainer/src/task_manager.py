import os
import json
import random
from flask import Flask, request, jsonify, render_template
from neo4j import GraphDatabase
from loguru import logger
import uuid
from src.llm_client import LLMClient
from src.PrologRuleGenerator import PrologRuleGenerator
from src.learning_agent import LearningAgent

app = Flask(__name__)

DATASET_DIR = "datasets/training/"  # Ensure dataset path is correct
HUMAN_VALIDATION_QUEUE = []  # Queue for human validation tasks

class TaskManager:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.llm_client = LLMClient()
        self.prolog_generator = PrologRuleGenerator()
        self.learning_agent = LearningAgent()
        logger.info("TaskManager initialized with multi-domain ontology and ARC support.")

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def get_random_task(self):
        """Selects a random ARC task file from the dataset directory."""
        files = [f.replace(".json", "") for f in os.listdir(DATASET_DIR) if f.endswith(".json")]
        return random.choice(files) if files else None

    def load_arc_task(self, task_name):
        """Loads an ARC dataset task from the datasets directory."""
        task_path = os.path.join(DATASET_DIR, f"{task_name}.json")
        if not os.path.exists(task_path):
            return {"error": f"Task '{task_name}' not found in dataset"}, 404
        with open(task_path, "r") as file:
            task_data = json.load(file)
        return task_data, 200

    def check_knowledge_graph(self, task_name):
        """Checks if a solution already exists in the Knowledge Graph."""
        with self.driver.session() as session:
            result = session.run(
                "MATCH (t:Task {name: $task_name}) RETURN t.solution AS solution, t.success AS success, t.prolog_rule AS prolog_rule",
                task_name=task_name
            )
            record = result.single()
            return record if record else None

    def log_counterexample(self, task_name, solution):
        """Logs failed AI solutions into the Knowledge Graph as counterexamples."""
        with self.driver.session() as session:
            session.run(
                "CREATE (t:Task {name: $task_name, failed_solution: $solution, success: False})",
                task_name=task_name, solution=json.dumps(solution)
            )

    def convert_cnl_to_prolog(self, cnl_rule):
        """Converts a Controlled Natural Language rule into Prolog using LLM."""
        prompt = f"Convert this Controlled Natural Language rule into Prolog: {cnl_rule}"
        response = self.llm_client.query_llm(prompt)
        return response.get("response", "Failed to generate Prolog")

    def validate_solution_with_prolog(self, prolog_rule):
        """Validates the AI solution using Prolog rule matching."""
        return self.prolog_generator.validate_rule_against_test_cases(prolog_rule, [])

    def log_to_knowledge_graph(self, task_name, solution, prolog_rule, success):
        """Stores AI solutions and Prolog-based reasoning in the Knowledge Graph."""
        with self.driver.session() as session:
            session.run(
                "CREATE (t:Task {name: $task_name, solution: $solution, prolog_rule: $prolog_rule, success: $success})",
                task_name=task_name, solution=json.dumps(solution), prolog_rule=prolog_rule, success=success
            )

    def attempt_solution(self, task_data, user_solution):
        """Uses AI to solve the ARC task with structured reasoning, checking KG first."""
        history = self.check_knowledge_graph(task_data["name"])
        if history and history["success"]:
            return history["solution"], True
        
        prompt = f"""
        You are an advanced AI trained in ARC pattern recognition. Given the following task, generate a logically structured solution:
        Task Data: {json.dumps(task_data, indent=2)}
        Your response should be a valid JSON output matching the expected format.
        """
        ai_response = self.llm_client.query_llm(prompt)
        try:
            solution = json.loads(ai_response.get("response", "[]"))
        except json.JSONDecodeError:
            solution = []  # Fallback to empty if LLM output is not structured correctly
        
        prolog_rule = self.convert_cnl_to_prolog(json.dumps(solution))
        if not self.validate_solution_with_prolog(prolog_rule):
            self.log_counterexample(task_data["name"], solution)
            return solution, False
        
        return solution, True

@app.route("/api/knowledge-graph", methods=["GET"])
def get_knowledge_graph():
    """Fetches stored AI task reasoning and Prolog rules from the Knowledge Graph."""
    task_manager = TaskManager()
    graph_data = task_manager.fetch_knowledge_graph()
    task_manager.close()
    return jsonify(graph_data)

@app.route("/knowledge-graph")
def knowledge_graph_page():
    """Renders the Popoto.js visualization page."""
    return render_template("knowledge_graph.html")

if __name__ == "__main__":
    logger.info("Starting Task Manager API with Popoto.js support.")
    app.run(host="0.0.0.0", port=5002)
