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

LIVE LINK OF MEETMIND:
https://meet-mind.streamlit.app/

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

 ## 📐 Code Architecture Walkthrough

### System Overview

MeetMind processes meeting transcripts through a **3-step specialized agent pipeline**. Each agent has a unique role, and the output of one agent becomes the input for the next. This ensures high-quality, validated outputs at each step.
  Raw Meeting Transcript (Input)
↓
[Context Agent]

Extracts: Summary, Conflicts, Key Decisions
Validates: JSON structure
↓
[Task Agent]
Receives: Context from Agent #1
Creates: Action Items, Owners, Deadlines
Validates: JSON structure
↓
[Communication Agent]
Receives: Tasks from Agent #2
Generates: Personalized follow-up emails
Outputs: Email drafts per stakeholder
↓
Executive Report + Follow-up Emails (Output)

---

### 1️⃣ Context Agent - Understanding the Meeting

**What it does:** Reads the raw transcript and extracts high-level meeting context.

**Why it's first:** Before we can create action items, we need to understand what happened in the meeting.

**Code Implementation:**
```python
import json
import google.generativeai as genai

async def context_agent(transcript: str) -> dict:
    """Extract high-level context from meeting transcript."""
    
    client = genai.Anthropic()
    
    response = client.messages.create(
        model="gemini-2.5-flash",
        max_tokens=1000,
        system="""You are an AI meeting analyst. Extract:
1. 3-sentence summary
2. Unresolved conflicts
3. Key decisions
4. All participants
Return ONLY valid JSON.""",
        messages=[{
            "role": "user",
            "content": f"""Analyze this meeting:

{transcript}

Return JSON:
{{
  "summary": "3-sentence summary",
  "conflicts": ["issue 1", "issue 2"],
  "key_decisions": ["decision 1"],
  "participants": ["name1", "name2"]
}}"""
        }]
    )
    
    # Extract JSON from response
    text = response.content[0].text
    json_start = text.find('{')
    json_end = text.rfind('}') + 1
    return json.loads(text[json_start:json_end])
```

**Key Design:**
- Specialized system prompt for focused output
- Enforces JSON structure
- Validates response before returning

---

### 2️⃣ Task Agent - Creating Action Items

**What it does:** Takes context from Agent #1 and creates action items with owners/deadlines.

**Why it's second:** Now we identify WHO does WHAT by WHEN.

**Code Implementation:**
```python
async def task_agent(context: dict, transcript: str) -> dict:
    """Generate action items from meeting context."""
    
    client = genai.Anthropic()
    
    response = client.messages.create(
        model="gemini-2.5-flash",
        max_tokens=1500,
        system="""Extract action items with owners, deadlines, and priorities.
Return ONLY valid JSON.""",
        messages=[{
            "role": "user",
            "content": f"""Context:
Summary: {context['summary']}
Participants: {', '.join(context['participants'])}

Extract action items from transcript:
{transcript}

Return JSON:
{{
  "action_items": [
    {{
      "description": "action",
      "owner": "person name",
      "deadline": "date/timeframe",
      "priority": "high/medium/low"
    }}
  ]
}}"""
        }]
    )
    
    text = response.content[0].text
    json_start = text.find('{')
    json_end = text.rfind('}') + 1
    return json.loads(text[json_start:json_end])
```

**Key Design:**
- Receives output from Agent #1 (shows pipeline)
- Structured fields ensure consistent output
- Each action item has clear owner and deadline

---

### 3️⃣ Communication Agent - Drafting Emails

**What it does:** Creates personalized follow-up emails for each participant.

**Why it's third:** Now we COMMUNICATE what needs to happen.

**Code Implementation:**
```python
async def communication_agent(tasks: dict, context: dict) -> dict:
    """Generate personalized follow-up emails."""
    
    client = genai.Anthropic()
    
    response = client.messages.create(
        model="gemini-2.5-flash",
        max_tokens=2000,
        system="""Create personalized follow-up emails for each participant.
Include only their action items. Be professional but friendly.
Return ONLY valid JSON.""",
        messages=[{
            "role": "user",
            "content": f"""Participants: {context['participants']}

Action Items:
{json.dumps(tasks['action_items'], indent=2)}

Create personalized emails for each person with their tasks.

Return JSON:
{{
  "emails": [
    {{
      "recipient": "Name",
      "subject": "Meeting Follow-up: Topic",
      "body": "Email content"
    }}
  ]
}}"""
        }]
    )
    
    text = response.content[0].text
    json_start = text.find('{')
    json_end = text.rfind('}') + 1
    return json.loads(text[json_start:json_end])
```

**Key Design:**
- Uses output from both Agent #1 and #2
- Personalized per participant
- Clear, actionable content

---

### The Complete Pipeline
```python
async def full_pipeline(transcript: str) -> dict:
    """Execute the complete 3-agent pipeline."""
    
    # Step 1: Extract context
    context = await context_agent(transcript)
    
    # Step 2: Create tasks (receives Step 1 output)
    tasks = await task_agent(context, transcript)
    
    # Step 3: Draft emails (receives Step 1 & 2 outputs)
    emails = await communication_agent(tasks, context)
    
    return {
        "context": context,
        "tasks": tasks,
        "emails": emails
    }
```

---

### Error Handling & Resilience

All agents include timeout and retry logic:
```python
import asyncio

async def call_agent_with_retry(agent_func, max_retries=3, timeout=30):
    """Call agent with retry on timeout."""
    
    for attempt in range(max_retries):
        try:
            result = await asyncio.wait_for(agent_func(), timeout=timeout)
            return result
        except asyncio.TimeoutError:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            raise

# Usage:
context = await call_agent_with_retry(
    lambda: context_agent(transcript)
)

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
