# ⚖️ Courtroom AI
### 🚀 Multi-Agent AI System for Legal Case Analysis, Courtroom Simulation & Judgment Assistance

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red?style=for-the-badge&logo=streamlit)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange?style=for-the-badge)
![LangChain](https://img.shields.io/badge/LangChain-LLM-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

</p>

---

# 📖 Overview

**Courtroom AI** is an AI-powered legal assistant that simulates a complete courtroom workflow using multiple intelligent AI agents.

The system accepts a legal complaint, analyzes the case, performs legal research, generates arguments for both prosecution and defense, provides expert consultation, and finally delivers an AI-generated judgment.

This project demonstrates the power of **Generative AI**, **Multi-Agent Systems**, **LLMs**, **LangGraph**, **FastAPI**, and **Streamlit** in the legal domain.

---

# 🎯 Key Features

✅ Complaint Analysis

✅ Intelligent Case Intake

✅ Entity Extraction

✅ Legal Research Agent

✅ Prosecutor AI

✅ Defense AI

✅ Legal Consultant

✅ Senior Legal Consultant

✅ AI Judge

✅ Court Reporter

✅ Multi-Agent Workflow using LangGraph

✅ FastAPI Backend

✅ Interactive Streamlit UI

---

# 🏛️ AI Agent Workflow

```text
                User Complaint
                      │
                      ▼
             Case Manager Agent
                      │
        ┌─────────────┼──────────────┐
        ▼             ▼              ▼
 Legal Research   Prosecutor     Defense
        │             │              │
        └──────┬──────┴──────┬───────┘
               ▼             ▼
      Legal Consultant   Senior Consultant
               │
               ▼
            AI Judge
               │
               ▼
          Court Reporter
               │
               ▼
         Final Case Report
```

---

# 🧠 Technologies Used

| Technology | Purpose |
|------------|----------|
| Python | Programming Language |
| FastAPI | Backend API |
| Streamlit | Frontend UI |
| LangGraph | Multi-Agent Orchestration |
| LangChain | LLM Framework |
| Ollama / OpenAI | Large Language Models |
| Pydantic | Data Validation |
| YAML | Configuration |
| REST API | Communication |

---

# 📂 Project Structure

```text
courtroom-ai/
│
├── backend/
│   ├── agents/
│   │      ├── case_manager.py
│   │      ├── prosecutor.py
│   │      ├── defense.py
│   │      ├── legal_research.py
│   │      ├── consultant.py
│   │      ├── top_consultant.py
│   │      ├── judge.py
│   │      └── reporter.py
│   │
│   ├── config.py
│   ├── llm.py
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── app.py
│   └── requirements.txt
│
└── README.md
```

---

# ⚙️ Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/Courtroom-AI.git

cd Courtroom-AI
```

---

## 2️⃣ Create Virtual Environment

Windows

```bash
python -m venv .venv

.venv\Scripts\activate
```

Linux / Mac

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

## 3️⃣ Install Backend Dependencies

```bash
cd backend

pip install -r requirements.txt
```

---

## 4️⃣ Install Frontend Dependencies

```bash
cd ../frontend

pip install -r requirements.txt
```

---

# ▶️ Run Backend

```bash
cd backend

uvicorn main:app --reload
```

Backend runs at

```
http://127.0.0.1:8000
```

---

# ▶️ Run Frontend

```bash
cd frontend

streamlit run app.py
```

---

# 🔄 Workflow

```text
User Complaint
      │
      ▼
Case Manager
      │
      ▼
Entity Extraction
      │
      ▼
Legal Research
      │
      ▼
Prosecutor
      │
      ▼
Defense
      │
      ▼
Legal Consultant
      │
      ▼
Senior Consultant
      │
      ▼
Judge
      │
      ▼
Court Reporter
      │
      ▼
Final Report
```

---

# 📸 Screenshots

## 🏠 Home Page

> Add screenshot here

```
screenshots/home.png
```

---

## 📝 Complaint Input

> Add screenshot here

```
screenshots/input.png
```

---

## ⚖️ AI Judgment

> Add screenshot here

```
screenshots/judgement.png
```

---

# 🌟 Future Improvements

- 🔍 RAG-based Legal Knowledge Base
- 📄 PDF Case Upload
- 🎙️ Voice Complaint Input
- 🌐 Multilingual Support
- ⚖️ Indian Penal Code Integration
- 📚 Legal Citation Generator
- 🔐 User Authentication
- ☁️ Cloud Deployment
- 🐳 Docker Support
- ☸ Kubernetes Deployment

---

# 💡 Use Cases

- Law Students
- Legal Research
- Court Simulation
- Legal Education
- AI Research
- Judicial Assistance
- Legal Tech Startups

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository

2. Create a feature branch

```bash
git checkout -b feature/new-feature
```

3. Commit your changes

```bash
git commit -m "Added new feature"
```

4. Push to GitHub

```bash
git push origin feature/new-feature
```

5. Open a Pull Request

---

# 📜 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

## **Nikesh Singh**

**MLOps | GenAI | Machine Learning Engineer**

- 💼 Multi-Agent AI Systems
- 🤖 Generative AI
- 📊 Machine Learning
- ⚙️ MLOps
- 🐳 Docker
- ☁️ FastAPI
- 🔗 LangGraph
- 🧠 LangChain

---

<p align="center">

### ⭐ If you like this project, don't forget to Star the repository!

**Made with ❤️ using Python, FastAPI, Streamlit & Generative AI**

</p>
