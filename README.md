# ARC Trainer Documentation

## Overview
The ARC Trainer system is designed to solve ARC (Abstraction and Reasoning Corpus) tasks by leveraging language games, Prolog reasoning, machine learning, and a Neo4j-backed knowledge graph. It supports dynamic rule generation, validation, and fine-tuning for generalization.

---

## Core Components

### 1. Frontend
- **index.html**: User interface for interacting with ARC tasks.
- **js/common.js**: Shared utilities for grid manipulation.
- **js/testing_interface.js**: Handles user inputs and task testing.
- **js/language_game.js**: Implements frontend logic for language games.
- **css/common.css**: General styles for the interface.
- **css/testing_interface.css**: Styles specific to ARC task interactions.

### 2. Backend
#### Core Functionality
- **app.py**: Main Flask application for routing and API handling.
- **graph_rag.py**: Neo4j-backed Knowledge Graph management.
- **language_game.py**: Handles reasoning and logic for language games.
- **grid.py**: Manages grid transformations and processing.
- **llm_client.py**: Interfaces with an LLM for reasoning and explanation generation.

#### New Modules
- **prolog_rule_generator.py**: Dynamically generates, validates, and stores Prolog rules.
- **counterexample_finder.py**: Identifies counterexamples for rule refinement.
- **kg_visualizer.py**: Visualizes the knowledge graph using NetworkX and Matplotlib.
- **metrics_dashboard.py**: Provides system and task performance metrics through an API.
- **language_game_trainer.py**: Trains machine learning models for specific language games.
- **llm_fine_tuner.py**: Fine-tunes pre-trained language models on ARC-specific tasks.
- **user_feedback.py**: Collects and processes user feedback for continuous improvement.
- **task_manager.py**: Manages task submission, processing, and status tracking.

---

## How to Use the ARC Trainer

### 1. Setup
#### Requirements:
- **Docker**: Install Docker for containerized deployment.
- **Python**: Version 3.9+.

#### Steps:
1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/ARC_Trainer.git
   cd ARC_Trainer
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure the environment**:
   - Update `config.json` with Neo4j credentials and other settings.

4. **Start services using Docker Compose**:
   ```bash
   docker-compose up --build
   ```

### 2. Workflow
1. **Submit Tasks**:
   - Use the Task Manager API (`POST /tasks`) to submit ARC tasks.

2. **Process Tasks**:
   - Monitor task progress through the Task Manager (`GET /tasks/<task_id>`).

3. **Refine Rules**:
   - Identify rule failures with the Counterexample Finder.
   - Update Prolog rules using the Rule Generator.

4. **Train Models**:
   - Train language games with `language_game_trainer.py`.
   - Fine-tune LLMs with `llm_fine_tuner.py`.

5. **Feedback Integration**:
   - Collect user feedback via the User Feedback API.
   - Incorporate feedback into rules and models.

6. **Visualize Knowledge**:
   - Use `kg_visualizer.py` to visualize relationships and dependencies.

---

## API Reference
### Task Manager
- **POST /tasks**: Submit a task.
- **GET /tasks/<task_id>**: Retrieve task status.

### User Feedback
- **POST /feedback**: Submit user feedback.
- **GET /feedback/<session_id>**: Retrieve feedback for a session.

### Metrics Dashboard
- **GET /metrics/tasks**: Fetch task metrics.
- **GET /metrics/system**: Fetch system performance metrics.

---

## Development Workflow
1. **Frontend Changes**:
   - Update `js` or `css` files for UI improvements.
   - Test changes locally by running `index.html` in a browser.

2. **Backend Updates**:
   - Update Python modules as needed.
   - Use `pytest` for testing backend changes.

3. **Knowledge Graph**:
   - Test Neo4j queries using the Neo4j browser.
   - Visualize changes with `kg_visualizer.py`.

4. **LLM Integration**:
   - Fine-tune models and validate outputs with real tasks.

---

## Future Enhancements
- Integrate Graph Neural Networks for enhanced reasoning.
- Add real-time feedback loops for dynamic rule adjustments.
- Improve scalability with distributed task processing.

---

## Troubleshooting
### Common Issues
- **Neo4j Connection**:
  - Ensure Neo4j is running and reachable at the configured host and port.
- **Task Failures**:
  - Check logs for task-specific errors.
  - Validate input formats and API payloads.
- **Rule Validation Issues**:
  - Use the Counterexample Finder to debug failing rules.

---

For questions or support, contact the development team.
