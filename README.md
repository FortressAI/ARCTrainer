# ARC Trainer: Advanced Reasoning Language Model (RLM) Framework

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

## 📌 Overview
The **ARC Trainer** is an **Advanced Reasoning Language Model (RLM) framework** that integrates **Knowledge Graphs (KGs), Prolog-based reasoning, and AI-to-AI debates** to create a self-improving AI reasoning system. Unlike black-box LLMs, ARC Trainer ensures **explainability, structured knowledge validation, and human oversight** before AI-generated knowledge is committed.

The system features **dual-mode AI evaluation**, supporting:
1. **ARC Dataset Mode** – Structured AI benchmarking using predefined logic tasks.
2. **Last Human Exam Mode** – Open-ended reasoning challenges where AI processes **visual inputs and generates logical puzzles**.

It also introduces a **multi-agent AI debate system**, where **AI models challenge and refine each other’s reasoning dynamically**.

---

## ✅ Key Features

### **1️⃣ Knowledge Graph-Driven AI Reasoning**
- Uses **Neo4j-based Knowledge Graphs** to store **validated AI knowledge**.
- Requires **human sign-off** before updating reasoning models.

### **2️⃣ Multi-Agent AI Debate System**
- AI agents **argue for and against reasoning rules**.
- Contradictions are **detected and logged** for refinement.
- Past debates are **stored in the Knowledge Graph for auditability**.

### **3️⃣ Dual-Mode AI Evaluation**
- **ARC Dataset Mode**: Tests structured AI logic through predefined challenges.
- **Last Human Exam Mode**: Uses **BLIP vision-language models** to generate reasoning challenges from images.

### **4️⃣ Visual Reasoning & Image Processing**
- AI can **process images using BLIP** to generate **structured logic puzzles**.
- Image-based reasoning tasks can be **stored and reviewed** in the Knowledge Graph.

### **5️⃣ Human-Governed Knowledge Export**
- **Humans validate AI-generated knowledge** before it is integrated into the KG.
- This ensures **AI remains accountable, explainable, and auditable**.

---

## 🛠 Installation

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/YOUR-USERNAME/ARC-Trainer.git
cd ARC-Trainer
```

### **2️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3️⃣ Set Up Neo4j Database**
1. Install **Neo4j** and start a local database.
2. Configure `.env` file with your **Neo4j credentials**:
```plaintext
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=yourpassword
```

### **4️⃣ Run ARC Trainer with Docker Compose**
```bash
docker-compose up --build
```

---

## 📌 Usage

### **1️⃣ Run the Last Human Test (Image-Based Reasoning)**
1. Start the **Flask backend**:
   ```bash
   python app.py
   ```
2. Open **http://localhost:5000** and **upload an image**.
3. AI generates a **logical reasoning challenge** based on the image.

### **2️⃣ Process an ARC Dataset Task**
```bash
python src/task_manager.py --load-task "example_task"
```
- Loads an **ARC logic puzzle** from the dataset.
- AI generates **solutions and validates them against KG rules**.

### **3️⃣ Start AI Multi-Agent Debate**
```bash
python src/GraphRAG.py --retrieve-debate-history "example_rule"
```
- Retrieves **past AI debates** from the KG.
- Allows for **AI reasoning refinement over time**.

---

## 🚀 Future Enhancements
- **Graph Neural Networks (GNNs)** for **automated pattern recognition**.
- **Integration of formal verification tools** for AI-generated knowledge.
- **Expanded AI-to-AI debate framework** to refine logic across multiple domains.

---

## 🤝 Contributing
We welcome **community contributions** to improve AI reasoning!  
- Fork the repository  
- Create a new branch (`git checkout -b feature-branch`)  
- Submit a **pull request**  

---

## 📜 License
This project is licensed under the **Apache 2.0 License**. See the [LICENSE](LICENSE) file for details.

---

## 📧 Contact
For inquiries, reach out via GitHub Issues or email **your.email@example.com**.
