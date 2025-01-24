# ARC Trainer: Advanced Reasoning Language Model (RLM) Framework

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

## 📌 Overview
The **ARC Trainer** is an **Advanced Reasoning Language Model (RLM) framework** that combines **symbolic logic, knowledge graphs, and language models** to create a self-improving AI system. It is designed to ensure **fairness, logical rigor, and transparency** in AI reasoning. 

Our system is **fully compliant** with the reasoning principles outlined in the **arXiv whitepaper 2501.11223: "Reasoning Language Models (RLMs): A Blueprint for Advanced AI Reasoning"**. 

Additionally, ARC Trainer now features **dual-mode AI evaluation**, supporting:
1. **ARC Dataset Mode** – Structured AI testing with predefined logic challenges.
2. **Humanity’s Last Exam Mode** – Open-ended, adversarial reasoning tests created by users.
3. **Multi-Agent Debate System** – AI vs. AI reasoning for rule validation and contradiction detection.

---

## ✅ Compliance with RLM Whitepaper (arXiv:2501.11223)
The ARC Trainer aligns with **all key principles of RLMs**:
1. **Multi-Step Causal Reasoning** – Ensures AI justifies conclusions step-by-step.
2. **Formal Verification** – Uses **Prolog logic and fairness constraints**.
3. **Counterfactual Reasoning** – AI considers **"what-if" scenarios** before accepting rules.
4. **Wittgensteinian Language Games** – Tracks **semantic meaning shifts** over time.
5. **Near Enemy Detection** – Prevents **rules that appear valid but are subtly flawed**.
6. **Knowledge Graph Integration** – Dynamically **updates AI logic** in Neo4j.
7. **Self-Improving AI** – Uses **iterative feedback loops** for rule refinement.
8. **Multi-Agent Debate System** – AI models debate and refine knowledge dynamically.

---

## 🚀 Key Features
### **🔹 1. Advanced Rule-Based AI (Prolog & LLM)**
- Implements **Aristotelian syllogistic logic** for structured reasoning.
- Uses **LLM-assisted rule validation** and **Socratic questioning**.
- Supports **formal verification** to detect inconsistencies.

### **🔹 2. Counterexample & Counterfactual Testing**
- AI generates **counterexamples** to test reasoning integrity.
- Uses **LLMs to generate hypothetical ("what-if") scenarios**.
- Ensures all rules hold under **alternative conditions**.

### **🔹 3. Fairness and Ethical AI Compliance**
- Implements **bias detection and fairness validation**.
- **Prevents rules from reinforcing discrimination or hidden biases**.
- Near Enemy Detection ensures **deceptive rules are flagged and refined**.

### **🔹 4. Knowledge Graph-Driven Learning**
- Stores reasoning in **Neo4j** for structured learning.
- Tracks **semantic meaning evolution** using **Wittgensteinian Language Games**.
- Self-improves over time **based on past rule evaluations**.

### **🔹 5. Multi-Agent Debate System for AI Self-Improvement**
- AI agents **challenge each other’s logic dynamically**.
- Logs **debate history** in **Neo4j for future refinement**.
- Enables **automated contradiction detection and resolution**.

### **🔹 6. Dual-Mode AI Evaluation**
- **ARC Dataset Mode** – Predefined logical challenges for AI benchmarking.
- **Humanity’s Last Exam Mode** – Open-ended, adversarial reasoning from human users.
- **Switch seamlessly** between both modes via the web UI.

---

## 🛠 Installation

### **🔹 1. Clone the Repository**
```bash
git clone https://github.com/YOUR-USERNAME/ARC-Trainer.git
cd ARC-Trainer
```

### **🔹 2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **🔹 3. Set Up Neo4j Database**
1. Install Neo4j and start a local database.
2. Configure `.env` file with your **Neo4j credentials**:
```plaintext
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=yourpassword
```

---

## 📌 Usage
### **🔹 1. Run the Counterexample Finder**
```bash
python src/CounterexampleFinder.py --rule "example_rule"
```
- Generates **counterexamples** and **counterfactual tests**.
- Logs failed cases to **Neo4j for refinement**.

### **🔹 2. Validate Reasoning in Prolog**
```bash
swipl -s src/aristotle_logic.pl
?- validate_rule(example_rule).
```
- Ensures all rules pass **multi-step causal reasoning**.
- Checks for **near enemy fallacies**.

### **🔹 3. Track Semantic Meaning Shifts**
```bash
python src/GraphRAG.py --track-rule "example_rule"
```
- Updates **rule meaning evolution** using **Wittgensteinian logic**.
- Ensures AI **adapts based on real-world changes**.

### **🔹 4. Start the Web UI**
```bash
python app.py
```
- Access **ARC Trainer’s Web UI** at `http://localhost:5000`
- Switch between **ARC Dataset Mode** and **Last Human Exam Mode**.

### **🔹 5. Run the Multi-Agent Debate System**
```bash
python src/GraphRAG.py --retrieve-debate-history "example_rule"
```
- Displays AI debate history stored in Neo4j.
- Allows **users to analyze contradictions and reasoning evolution**.

---

## 🚀 Future Enhancements
- **Graph Neural Networks (GNNs)** for improved **pattern recognition**.
- **Automated Formal Verification** through **proof assistants**.
- **Extended Domain Applications**: Law, Healthcare, and Ethics.
- **Multi-Agent Debate Expansion** – Allowing more AI perspectives.

---

## 🤝 Contributing
We welcome **community contributions** to improve reasoning AI!  
- Fork the repository  
- Create a new branch (`git checkout -b feature-branch`)  
- Submit a **pull request**  

---

## 📜 License
This project is licensed under the **Apache 2.0 License**. See the [LICENSE](LICENSE) file for details.

---

## 📧 Contact
For inquiries, reach out via GitHub Issues or email **your.email@example.com**.
