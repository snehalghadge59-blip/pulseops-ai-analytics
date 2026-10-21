# ⚡ PulseOps AI: Autonomous E-Commerce & Supply Chain Intelligence Agent

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io)
[![SQLite](https://img.shields.io/badge/Database-SQLite%20Relational-003B57.svg?logo=sqlite&logoColor=white)](https://sqlite.org)
[![Plotly](https://img.shields.io/badge/Visualization-Plotly%20Interactive-3F4F75.svg?logo=plotly&logoColor=white)](https://plotly.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **PulseOps AI** is an enterprise-grade autonomous Business Intelligence (BI) and Conversational Data Agent designed for modern e-commerce and logistics operations. It bridges the gap between raw relational databases and executive decision-making by transforming natural language questions into validated, high-performance SQL, auto-generating interactive Plotly visualizations, and synthesizing weekly executive briefings (PDF & Markdown) with actionable dollar-impact recommendations.

---

## 📌 Executive Summary & Business Impact

| Operational Metric | Pre-PulseOps (Manual Reporting) | With PulseOps AI Agent |
| :--- | :--- | :--- |
| **Ad-Hoc Query Turnaround** | 4–6 Hours (SQL Request Queue) | **< 2 Seconds (Instant Conversational BI)** |
| **SLA Breach Detection** | End-of-Month Retrospective | **Real-Time Carrier Delay & Penalty Tracking** |
| **Executive Reporting Effort** | 12 Hours / Week in Excel/Slides | **1-Click Automated Institutional PDF Compilation** |
| **Query Security & Guardrails** | Manual review | **Strict AST AST Read-Only Validation & Zero SQL Injection** |

---

## 🏗️ Architecture & Data Pipeline

```mermaid
graph TD
    User([Executive / Stakeholder]) -->|Natural Language Inquiry| UI[Streamlit Interactive Glassmorphic UI]
    UI --> Agent[AIAgent Orchestrator]
    
    subgraph AI & Safety Pipeline
        Agent --> NL2SQL[Semantic Planner & Schema Introspector]
        NL2SQL --> Guardrails[AST SQL Safety Validator]
        Guardrails -->|Blocks Destructive Ops| Security[SQL Injection Prevention]
    end
    
    subgraph Data & Analytics Warehouse
        Guardrails -->|Validated Read-Only SQL| Engine[(Relational DB: SQLite/PostgreSQL)]
        Engine --> Analytics[Enterprise Analytics Engine]
        Analytics --> Cohorts[Monthly Cohort Retention Matrix]
        Analytics --> RFM[Customer RFM Window Functions]
        Analytics --> SLA[Logistics Carrier SLA Breaches]
    end
    
    subgraph Synthesis & Delivery
        Analytics --> Visuals[Dynamic Plotly Charts]
        Analytics --> Synthesizer[Executive Insight Synthesizer]
        Synthesizer --> Briefing[1-Click ReportLab PDF & Markdown Studio]
    end
    
    Visuals --> UI
    Synthesizer --> UI
    Briefing --> UI
```

---

## 🚀 Key Engineering Highlights

### 1. 💬 Conversational BI & NL-to-SQL Engine
* **Zero-Cost Heuristic Planner + Optional Generative LLM:** Operates 100% out-of-the-box using deterministic semantic intent mapping, with optional drop-in support for OpenAI GPT-4o / Gemini models.
* **Database Schema Introspector:** Dynamically inspects tables, column types, and foreign key relationships to prevent hallucinated table names.
* **SQL Safety Engine:** Rigorous AST check that strictly permits `SELECT` / `WITH` statements and rejects `DROP`, `DELETE`, `UPDATE`, `ALTER`, or `INSERT` attempts.

### 2. 📊 Advanced Enterprise SQL Analytics
* **Cohort Retention Matrix:** Uses multi-step SQL Common Table Expressions (CTEs) to track monthly user retention decay up to 6 months post-acquisition.
* **RFM Customer Segmentation:** Leverages SQL Window Functions (`NTILE(4) OVER (ORDER BY ...)`) to segment accounts into *Champions*, *Loyal*, *At Risk*, and *Hibernating*.
* **Carrier SLA & Penalty Quantification:** Aggregates delivery transit times, computes delay percentage per carrier, and models estimated freight dispute penalties.

### 3. 📑 Autonomous Executive Briefing Studio
* **Instant ReportLab PDF Generation:** Compiles a publication-ready corporate PDF report complete with KPI tables, risk flags, and management directives.
* **Markdown Export:** Formatted for instant copy-pasting into Jira, Slack, or Notion.

---

## 📂 Repository Structure

```
pulseops-ai-analytics/
├── data/
│   ├── seed_data.py               # Generates 2,500+ realistic relational orders, deliveries, and customers
│   └── ecommerce_logistics.db     # SQLite relational database
├── src/
│   ├── __init__.py
│   ├── database.py                # Schema reflection and AST-safe query execution
│   ├── analytics.py               # Advanced CTEs, Cohort retention, and RFM models
│   ├── agent.py                   # NL-to-SQL parsing and insight synthesis
│   └── reporter.py                # ReportLab PDF & Markdown briefing generator
├── tests/
│   ├── __init__.py
│   └── test_agent.py              # Automated test suite (Database, Guardrails, KPIs)
├── app.py                         # Streamlit interactive application
├── requirements.txt               # Dependency manifest
├── run.bat                        # 1-click Windows starter
└── README.md                      # Architecture documentation
```

---

## ⚡ Quick Start (Run Locally in 60 Seconds)

### 1. Clone Repository & Install Dependencies
```bash
git clone https://github.com/snehalghadge59-blip/pulseops-ai-analytics.git
cd pulseops-ai-analytics
pip install -r requirements.txt
```

### 2. Seed Relational Database
```bash
python data/seed_data.py
```

### 3. Run Automated Tests
```bash
python -m unittest tests/test_agent.py
```

### 4. Launch Application
```bash
streamlit run app.py
```
*Or double-click `run.bat` on Windows.*

The dashboard will open at `http://localhost:8501`.

---

## 🎯 Sample Questions for Conversational BI
* *"Which carrier has the worst delivery delay rate and lowest CSAT?"*
* *"Top products by revenue and gross profit margin"*
* *"Monthly revenue trend and order count over time"*
* *"Customer segment revenue comparison"*
* *"Delayed vs on-time delivery impact on customer ratings"*

---

## 💼 Resume & Interview Talking Points

**Project Title:** PulseOps AI — Autonomous BI & Supply Chain Analytics Agent  
**Bullet Points for Resume:**
* *Architected an autonomous conversational BI agent using Python, SQLite, and Streamlit, enabling non-technical stakeholders to perform ad-hoc SQL inquiries via natural language in < 2 seconds.*
* *Engineered advanced SQL analytical models utilizing multi-level CTEs and Window Functions (`NTILE`, `RANK`) to calculate 6-month customer cohort retention matrices and RFM segmentation tiers.*
* *Built an automated executive briefing engine using ReportLab, compiling weekly operational reviews and carrier SLA breach risk assessments into production-grade PDFs.*
* *Implemented an AST-level SQL validation layer to prevent SQL injection and guarantee strict read-only execution across a 2,500+ multi-table relational schema.*

---

## 📜 License
Distributed under the MIT License. Built with ❤️ by **Snehal Ghadge**.
