<div align="center">
  <img src="https://img.shields.io/badge/Status-Live-success?style=for-the-badge&logo=rocket" />
  <img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/AI-Gemini%202.5%20Flash-4285F4?style=for-the-badge&logo=google&logoColor=white" />
  <h1>🧠 MeetMind</h1>
  <h3>Turn Any Meeting Into Action — Automatically.</h3>
</div>

---

**MeetMind** is an enterprise-grade AI Productivity Agent built to eliminate the loss of critical information that happens post-meeting. Instead of relying on bloated, generalized summary prompt walls, MeetMind is powered by an advanced **Multi-Agent Chain** using Google's fastest `gemini-2.5-flash` endpoint. It processes your internal meeting transcripts and outputs highly structured, immediately actionable data.

![MeetMind Screenshot Placeholder](https://via.placeholder.com/1000x500.png?text=MeetMind+App+Screenshot)

## ✨ Why MeetMind?
Unproductive meetings cost businesses billions every year. The absolute biggest leak is **follow-through**. Valuable insights dissolve into thin air because action items aren't explicitly tracked and dedicated follow-up emails are notoriously postponed. **MeetMind solves this instantly.**

It features a heavily customized **Obsidian Green & Bone** glassmorphic dark-theme UI with pure developer-focused aesthetic cues, making your data analysis visually striking.

## 🚀 Key Features
- 🔄 **3-Step Agentic Pipeline**: Different specialized prompts are fed down a seamless queue ensuring perfect structured JSON constraint extractions.
  - **Context Agent**: Condenses heavy jargon into 3-sentence summaries and flags unresolved conflicts.
  - **Task Agent**: Maps precise action items, assigning explicit owners, strict deadlines, and visual priority badges.
  - **Communication Agent**: Auto-drafts personalized, pre-written follow-up communications per stakeholder.
- 🎯 **Meeting Health Score algorithm**: Get graded (X/10) dynamically on *Clarity*, *Decisiveness*, and *Accountability*.
- 📥 **Markdown Exporter**: Download the finalized executive report straight to your local machine.

## 🛠 Tech Stack
- **Dashboard UI**: Python & Streamlit 
- **Language Model**: Google Gemini API (`gemini-2.5-flash` natively enforcing JSON structured mode)
- **Data Formatting**: Pandas

## 💻 How to Run Locally

You can launch MeetMind on your local environment in minutes!

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Rohittt29/MeetMind.git
   cd MeetMind
   ```

2. **Initialize a virtual environment (Recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows PowerShell use: venv\Scripts\activate
   ```

3. **Install Core Dependencies:**
   ```bash
   python -m pip install -r requirements.txt
   ```

4. **Environment Secrets Config:**
   Simply create a `.env` file in the root project directory and securely place your Google Gemini key:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

5. **Boot the App:**
   ```bash
   python -m streamlit run app.py
   ```

---
<div align="center">
  <b>Built by Rohit Kumbhar · MeetMind © 2026</b>
</div>
