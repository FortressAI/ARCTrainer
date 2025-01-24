from flask import Flask, render_template, send_from_directory, jsonify, request
from llm_client import LLM  # Assuming LLM integration for AI debate responses

app = Flask(__name__, template_folder="public", static_folder="public")

# Serve UI Pages
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/challenge')
def challenge():
    return render_template("challenge.html")

@app.route('/simulation')
def simulation():
    return render_template("simulation.html")

@app.route('/leaderboard')
def leaderboard():
    return render_template("leaderboard.html")

# Serve static files
@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('public/css', path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('public/js', path)

# API Endpoint: AI Multi-Agent Debate
@app.route('/api/debate', methods=['POST'])
def start_debate():
    data = request.get_json()
    rule = data.get("rule")

    # Simulate AI Agents debating the rule
    agent1_response = LLM.ask(f"Defend this rule: {rule}")
    agent2_response = LLM.ask(f"Challenge this rule: {rule}")

    # Evaluate contradictions
    contradiction = LLM.ask(f"Does '{agent1_response}' contradict '{agent2_response}'?")

    return jsonify({
        "rule": rule,
        "agent1": agent1_response,
        "agent2": agent2_response,
        "contradiction_found": contradiction.lower() == "yes"
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
