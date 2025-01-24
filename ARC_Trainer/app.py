from flask import Flask, render_template, send_from_directory, jsonify, request

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

# API Endpoint: Start an ARC Dataset Challenge
@app.route('/api/arc-test', methods=['POST'])
def arc_test():
    arc_challenge = {
        "message": "Solve this structured problem: What is the next number in the sequence 2, 4, 8, 16, ?"
    }
    return jsonify(arc_challenge)

# API Endpoint: Start a Last Human Exam Challenge
@app.route('/api/start-challenge', methods=['POST'])
def start_challenge():
    data = request.get_json()
    challenge_input = data.get("input", "")
    response = {
        "message": f"AI is processing your challenge: {challenge_input}"
    }
    return jsonify(response)

# API Endpoint: Get Leaderboard Data
@app.route('/api/get-leaderboard', methods=['GET'])
def get_leaderboard():
    leaderboard_data = [
        {"user": "Alice", "score": 95},
        {"user": "Bob", "score": 88},
        {"user": "Charlie", "score": 82}
    ]
    return jsonify(leaderboard_data)

# API Endpoint: Run an AI Simulation
@app.route('/api/simulate', methods=['POST'])
def simulate():
    data = request.get_json()
    scenario = data.get("scenario", "default scenario")
    return jsonify({"simulation": f"AI's simulated response for scenario: {scenario}"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
