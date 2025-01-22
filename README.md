# ARC Trainer System - Deep Dive Documentation

## 🚀 Introduction
The **ARC Trainer System** is an **AI-driven ontology processing framework** that integrates:
- **Ontology Rule Processing** (Legal, Healthcare, AI Ethics, Finance, Education, Warfare)
- **Neo4j Knowledge Graphs** for structured ontology storage
- **Prolog-based reasoning engine** for validation & rule learning
- **AI-Driven Refinement** using LLMs (GPT-4)
- **Multi-Format Ontology Export** (CSV, JSON, GraphML, Neo4j)

---

## 📌 Features
✔ **AI-Powered Ontology Learning**  
✔ **Multi-Domain Support** (Legal, Healthcare, AI Ethics, Finance, Education, Warfare)  
✔ **CNL-to-Prolog Conversion**  
✔ **Graph-Based Storage & Retrieval**  
✔ **Counterexample Generation & Refinement**  
✔ **User Feedback-Driven Rule Corrections**  
✔ **Real-Time API Endpoints for Rule Processing**  

---

## 🤖 What is Controlled Natural Language (CNL)?
### **CNL Overview**
Controlled Natural Language (CNL) is a simplified subset of natural language that is structured for easy processing by machines **while remaining human-readable**.  
- Example: **"A contract is a legally binding agreement between two or more parties."**  
- Converted to Prolog:  
  ```prolog
  contract(X, Y) :- legally_binding_agreement(X, Y).
  ```

### **Why CNL Matters?**
✔ **Bridges human language & AI**  
✔ **Ensures logical consistency**  
✔ **Easier for non-technical users to define rules**  

### **How CNL Works in ARC Trainer?**
1️⃣ **User submits a CNL ontology rule**  
2️⃣ **LLM converts it into Prolog logic**  
3️⃣ **Ontology system stores and validates the rule**  
4️⃣ **The system refines rules based on feedback & contradictions**  

---

## 🛠️ Installation Guide

### **1️⃣ Prerequisites**
Ensure you have the following installed:
- Python 3.8+
- Neo4j (Graph Database)
- OpenAI API Key (For LLM Processing)

### **2️⃣ Clone the Repository**
```bash
git clone https://github.com/your-repo/ARC_Trainer.git
cd ARC_Trainer
```

### **3️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4️⃣ Set Up Environment Variables**
Rename the `.env.example` file to `.env` and update your credentials:
```bash
cp .env.example .env
nano .env  # Edit and update your credentials
```

### **5️⃣ Start Neo4j**
```bash
neo4j start
```

### **6️⃣ Run the Application**
```bash
python task_manager.py
```

---

## 📡 API Endpoints

### 🔹 **1. Submit an Ontology Rule**
- **Endpoint:** `POST /tasks`
- **Description:** Stores a new ontology rule in Neo4j.
- **Request Example:**
```json
{
    "cnl_rule": "A contract is a legally binding agreement between two or more parties.",
    "domain": "legal"
}
```
- **Response Example:**
```json
{
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "queued",
    "prolog_rule": "contract(X, Y) :- legally_binding_agreement(X, Y)."
}
```

---

### 🔹 **2. Retrieve Ontology Rules**
- **Endpoint:** `GET /tasks/{task_id}`
- **Description:** Fetches the status and details of an ontology rule.
- **Response Example:**
```json
{
    "status": "validated",
    "cnl_rule": "A contract is a legally binding agreement between two or more parties.",
    "prolog_rule": "contract(X, Y) :- legally_binding_agreement(X, Y).",
    "domain": "legal"
}
```

---

### 🔹 **3. Validate Ontology Rule**
- **Endpoint:** `POST /validate_rule`
- **Description:** Checks if an ontology rule is logically consistent.
- **Request Example:**
```json
{
    "rule": "contract(X, Y) :- legally_binding_agreement(X, Y)."
}
```
- **Response Example:**
```json
{
    "status": "valid"
}
```

---

### 🔹 **4. Submit User Feedback**
- **Endpoint:** `POST /feedback`
- **Description:** Allows users to suggest ontology rule corrections.
- **Request Example:**
```json
{
    "rule_id": "legal_rule_001",
    "feedback_text": "This rule should specify 'written agreements only.'",
    "user_id": "user_123",
    "domain": "legal"
}
```

---

### 🔹 **5. Export Ontology Data**
- **Endpoint:** `GET /export`
- **Query Parameters:**  
  - `domain` (e.g., `legal`, `healthcare`)  
  - `format` (csv, json, graphml, neo4j)
- **Example:**  
```bash
curl "http://localhost:5005/export?domain=ai_ethics&format=json"
```

---

## 📊 Metrics Dashboard

### 🔹 **View Ontology Analytics**
- **Endpoint:** `GET /metrics`
- **Tracks:**
  - Rule updates per domain
  - Feedback activity (pending vs processed)
  - Rule validation pass/fail rates

---

## 🔧 Advanced Configuration

### **`.env` Configuration Example**
```ini
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
OPENAI_API_KEY=your_openai_api_key
ONTOLOGY_DOMAINS=legal,healthcare,education,ai_ethics,finance,warfare,general
EXPORT_DIR=exports/
LOG_LEVEL=INFO
```

---

## 🤝 Contributing
We welcome contributions! To contribute:  
1️⃣ Fork the repository  
2️⃣ Create a feature branch (`git checkout -b feature-name`)  
3️⃣ Commit changes (`git commit -m "Added feature"`)  
4️⃣ Push the branch (`git push origin feature-name`)  
5️⃣ Open a pull request  

---

## 📝 License
This project is licensed under the **Apache 2.0 License**.  

---

## 📞 Contact
For support, reach out to **richard_gillespie@live.com**.  

🚀 **Happy Ontology Engineering!**  
