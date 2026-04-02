# 🧠 Conflict Intelligence Dashboard: Clickbait, Events & Risk Analysis

An end-to-end NLP-powered system for analyzing geopolitical news data, focusing on:
- 📊 Event Detection
- ⚠️ Risk Modeling
- 📰 Clickbait Detection
- 🌍 Actor & Country Interaction Graphs

Built using Python, Machine Learning, and deployed via Streamlit.

---

## 🚀 Features

### 🔍 1. Event Detection
- Clusters news articles into events using:
  - Sentence embeddings (MiniLM)
  - Cosine similarity
  - Agglomerative clustering
- Automatically identifies major geopolitical events

---

### ⚠️ 2. Risk Analysis
- Keyword-based scoring system for conflict intensity
- Machine learning model (Logistic Regression) for classification
- Categorizes news into **LOW / MEDIUM risk**

---

### 📰 3. Clickbait Detection
- Hybrid NLP approach:
  - Transformer-based classification
  - Headline + content analysis
- Generates:
  - Clickbait label
  - Confidence score
- Visual dashboard for insights

---

### 🌍 4. Actor & Country Network
- Extracts entities using NLP (spaCy)
- Builds interaction graph using NetworkX
- Visualizes geopolitical relationships

---

### 📊 5. Interactive Dashboard
- Built with **Streamlit**
- Includes:
  - Clickbait distribution
  - Confidence analysis
  - Top headlines
  - Graph-based insights

---

## 🛠️ Tech Stack

- **Python**
- **Pandas, NumPy**
- **Scikit-learn**
- **Sentence Transformers**
- **Hugging Face Transformers**
- **spaCy**
- **NetworkX**
- **Matplotlib / Seaborn / Plotly**
- **Streamlit**

---


---

## ⚙️ Installation

```bash
git clone https:[//github.com/Bishal-bit/osint_monitor.git]
cd osint_monitor
pip install -r requirements.txt
