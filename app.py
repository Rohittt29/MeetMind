import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import os
from dotenv import load_dotenv

load_dotenv()

# App Setup
st.set_page_config(page_title="MeetMind — Agentic AI", layout="wide")

def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
            color: #E3E3DE;
        }
        
        .stApp {
            background-color: #0B100E;
        }

        /* Top Navbar */
        .custom-navbar {
            background-color: rgba(11, 16, 14, 0.85);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: -3rem -4rem 2rem -4rem;
            position: sticky;
            top: 0;
            z-index: 999;
            border-bottom: 1px solid rgba(125, 140, 124, 0.2);
        }
        .nav-logo {
            font-size: 1.5rem;
            font-weight: 700;
            color: #E3E3DE;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            letter-spacing: -0.02em;
        }
        .nav-links {
            display: flex;
            gap: 2rem;
        }
        .nav-links a {
            text-decoration: none;
            color: #7D8C7C;
            font-weight: 500;
            font-size: 1rem;
            transition: color 0.2s, text-shadow 0.2s;
        }
        .nav-links a:hover {
            color: #E3E3DE;
            text-shadow: 0 0 10px rgba(227, 227, 222, 0.3);
        }
        
        /* Modern Button styling + Download Button */
        .stButton>button, [data-testid="stDownloadButton"] button {
            background-color: #7D8C7C !important;
            color: #000000 !important;
            border-radius: 6px !important;
            border: none !important;
            padding: 0.5rem 1rem !important;
            font-weight: 600 !important;
            transition: all 0.2s !important;
        }
        .stButton>button *, [data-testid="stDownloadButton"] button * {
            color: #000000 !important;
        }
        .stButton>button:hover, [data-testid="stDownloadButton"] button:hover {
            background-color: #E3E3DE !important;
            box-shadow: 0 4px 12px rgba(125, 140, 124, 0.2) !important;
            transform: translateY(-1px);
        }

        /* Cards styling */
        .meetmind-card {
            background-color: #1A1F1D;
            border-radius: 8px;
            padding: 1.5rem;
            border: 1px solid rgba(125, 140, 124, 0.15);
            margin-bottom: 1.5rem;
            transition: border-color 0.2s;
        }
        .meetmind-card:hover {
            border-color: rgba(125, 140, 124, 0.4);
        }
        
        .card-title {
            color: #E3E3DE;
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1rem;
            border-bottom: 1px solid rgba(125, 140, 124, 0.15);
            padding-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* Hide default headers and footers */
        header[data-testid="stHeader"] { display: none !important; }
        footer {
            display: none !important;
        }
        .block-container {
            padding-top: 3rem !important;
        }
        
        /* Priority Badges */
        .badge {
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
        }
        .badge-high { background-color: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); }
        .badge-medium { background-color: rgba(245, 158, 11, 0.1); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.2); }
        .badge-low { background-color: rgba(34, 197, 94, 0.1); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.2); }
        
        .custom-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }
        .custom-table th {
            background-color: #0B100E;
            text-align: left;
            padding: 12px;
            font-weight: 600;
            color: #7D8C7C;
            border-bottom: 1px solid rgba(125, 140, 124, 0.2);
        }
        .custom-table td {
            padding: 12px;
            border-bottom: 1px solid rgba(125, 140, 124, 0.1);
            color: #E3E3DE;
        }
        
        /* Force text colors even if user system is in dark mode */
        p, li, span { color: #7D8C7C !important; }
        h1, h2, h3, h4, h5, h6 { color: #E3E3DE !important; letter-spacing: -0.02em !important; }
        .stException *, .stMarkdown * { color: #E3E3DE !important; }

        details > summary { list-style: none; }
        details > summary::-webkit-details-marker { display: none; }
        </style>
    """, unsafe_allow_html=True)

def render_navbar():
    st.markdown("""
    <div class="custom-navbar">
        <div class="nav-logo">MeetMind</div>
        <div class="nav-links">
            <a href="?page=Home" target="_self">Home</a>
            <a href="?page=How+It+Works" target="_self">How It Works</a>
            <a href="?page=About" target="_self">About</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

SAMPLES = {
    "Team Standup": "Alice: Hi guys, let's do the standup. My update: I finished the frontend login. Today I'll work on the API integration but I'm blocked on the auth token from Bob. Bob: Yeah, sorry about that, I'll send you the token by noon today. I'm finishing the database schema. Charlie: I'm working on the design system. Do we want to use React or Vue? Alice: I thought we agreed on React? Charlie: We didn't finalize it. Let's decide tomorrow. Bob: Ok.",
    "Client Call": "Client (Sarah): We reviewed the alpha build. We like the dashboard but we need the export to PDF feature before we can launch. Can we get that by Friday? PM (Mark): Export to PDF is tricky. Dev (John): I can probably do a basic PDF export by Friday, but it won't have the custom charts yet. Sarah: That's fine for now, we just need the data tables. Mark: Great, John will handle the basic PDF export by Friday. Also, Sarah, did your team approve the new pricing tier? Sarah: Not yet, our legal team is still reviewing it.",
    "Strategy Meeting": "CEO (David): We need to increase Q3 revenue. Marketing, what's the plan? CMO (Lisa): We're launching the summer campaign. We need $50k budget. CFO (Tom): We only have $30k allocated for marketing. David: We need to figure this out. Can we reallocate from HR? HR (Anna): We have $20k we haven't used, but we need it for hiring. David: Let's hold off on hiring for two weeks. Tom, move the $20k to marketing by tomorrow. Tom: Understood. Lisa, send me the campaign brief by EOD. Lisa: Will do."
}

def extract_json(response_text):
    text = response_text.strip()
    if text.startswith("```json"): text = text[7:]
    elif text.startswith("```"): text = text[3:]
    if text.endswith("```"): text = text[:-3]
    try:
        return json.loads(text.strip())
    except Exception as e:
        return {"error": f"Failed to parse JSON: {e}"}

def run_agentic_chain(transcript, meeting_type):
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
    
    # Step 1
    prompt1 = f"""You are a Meeting Intelligence Agent. Read this {meeting_type} transcript carefully.
    Extract: 
    1) A concise summary (3-5 sentences)
    2) All action items with owner name, deadline, and priority (High, Medium, Low)
    3) Any unresolved conflicts or open questions. 
    Return clean JSON with keys: 'summary' (string), 'action_items' (array of objects with 'task', 'owner', 'deadline', 'priority'), 'conflicts' (array of strings).
    Transcript:
    {transcript}"""
    
    res1 = model.generate_content(prompt1)
    data1 = extract_json(res1.text)
    
    # Step 2
    action_items_str = json.dumps(data1.get('action_items', []))
    prompt2 = f"""You are an Executive Communication Agent. 
    Based on these action items: {action_items_str}, draft a personalized follow-up email for each unique owner. 
    Each email should be professional, mention only their specific tasks, and have a clear subject line. 
    Return clean JSON with exactly this key: 'emails' (array of objects with 'owner', 'subject', 'body')."""
    
    res2 = model.generate_content(prompt2)
    data2 = extract_json(res2.text)
    
    # Step 3
    summary_str = data1.get('summary', '')
    prompt3 = f"""You are a Meeting Quality Analyst. 
    Based on this meeting summary and action items:
    Summary: {summary_str}
    Action Items: {action_items_str}
    
    Score the meeting out of 10 on three dimensions: 
    clarity (was communication clear?), decisiveness (were firm decisions made?), accountability (were clear owners assigned?). 
    Return clean JSON with exactly these keys: 'clarity_score' (number 0-10), 'decisiveness_score' (number 0-10), 'accountability_score' (number 0-10), 'overall_score' (number 0-10), 'one_line_verdict' (string)."""
    
    res3 = model.generate_content(prompt3)
    data3 = extract_json(res3.text)
    
    return data1, data2, data3

def generate_markdown_report(data1, data2, data3):
    md = "# MeetMind Analysis Report\n\n"
    md += f"## Health Score: {data3.get('overall_score', 0)}/10\n"
    md += f"*{data3.get('one_line_verdict', '')}*\n\n"
    
    md += "## Summary\n"
    md += f"{data1.get('summary', '')}\n\n"
    
    md += "## Action Items\n"
    for item in data1.get('action_items', []):
        md += f"- **{item.get('owner', 'Unknown')}**: {item.get('task', '')} (Deadline: {item.get('deadline', '')}, Priority: {item.get('priority', '')})\n"
    
    md += "\n## Unresolved Conflicts / Open Questions\n"
    conflicts = data1.get('conflicts', [])
    if conflicts:
        for c in conflicts:
            md += f"- {c}\n"
    else:
        md += "None detected.\n"
        
    md += "\n## Email Drafts\n"
    for e in data2.get('emails', []):
        md += f"### To: {e.get('owner', 'Unknown')}\n"
        md += f"**Subject**: {e.get('subject', '')}\n\n"
        md += f"{e.get('body', '')}\n\n"
        md += "---\n"
        
    md += "\n*Generated by MeetMind AI*"
    return md

def render_home():
    st.markdown("""
    <div style="text-align: center; padding: 2rem 1rem 3rem 1rem;">
        <h1 style="color: #E3E3DE; font-size: 3.5rem; font-weight: 800; margin-bottom: 1rem;">Turn Any Meeting Into Action — Automatically</h1>
        <p style="color: #7D8C7C; font-size: 1.25rem; max-width: 800px; margin: 0 auto 2.5rem auto;">Paste your meeting transcript and let AI handle the rest — summaries, action items, emails, and conflict flags. All in seconds.</p>
        <a href="#analysis-section" style="background-color: #7D8C7C; color: #0B100E; padding: 0.8rem 1.5rem; border-radius: 6px; font-weight: 600; font-size: 1.125rem; text-decoration: none; border: 1px solid transparent; transition: all 0.2s; display: inline-block;">Analyze My Meeting</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div id='analysis-section'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    if 'transcript_input' not in st.session_state:
        st.session_state.transcript_input = ""
        
    with col1:
        transcript = st.text_area("Paste Your Meeting Transcript Here", value=st.session_state.transcript_input, height=250, placeholder="Example: Hey team, let's sync up on the Q3 roadmap...")
    with col2:
        st.markdown("<div style='margin-bottom: 27px'></div>", unsafe_allow_html=True)
        sample_choice = st.selectbox("Load Sample Transcript", ["Select...", "Team Standup", "Client Call", "Strategy Meeting"])
        if sample_choice != "Select...":
            if st.session_state.get('last_sample') != sample_choice:
                st.session_state.transcript_input = SAMPLES[sample_choice]
                st.session_state.last_sample = sample_choice
                st.rerun()

        meeting_type = st.selectbox("Meeting Type", ["Team Standup", "Client Call", "Strategy Meeting", "1-on-1"])
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Run MeetMind Agent", type="primary", use_container_width=True):
        if not os.getenv("GEMINI_API_KEY"):
            st.error("Please configure your GEMINI_API_KEY in the environment or `.env` file.")
            st.stop()
        if not transcript.strip():
            st.warning("Please paste a transcript to analyze.")
            st.stop()
            
        with st.status("🧠 Running MeetMind Agent...", expanded=True) as status:
            try:
                st.write("Step 1: Understanding transcript and extracting entities...")
                data1, data2, data3 = run_agentic_chain(transcript, meeting_type)
                
                status.update(label="✨ Analysis Complete!", state="complete", expanded=False)
                
                st.session_state.analysis_results = {
                    "step1": data1,
                    "step2": data2,
                    "step3": data3
                }
            except Exception as e:
                status.update(label=f"❌ Error: {str(e)}", state="error", expanded=False)
                st.stop()
                
    if 'analysis_results' in st.session_state:
        res1 = st.session_state.analysis_results['step1']
        res2 = st.session_state.analysis_results['step2']
        res3 = st.session_state.analysis_results['step3']
        
        st.markdown("<hr style='margin: 3rem 0; border: none; border-top: 1px solid rgba(125, 140, 124, 0.2);'>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: #E3E3DE; margin-bottom: 2rem;'>Analysis Results</h2>", unsafe_allow_html=True)
        
        md_report = generate_markdown_report(res1, res2, res3)
        st.download_button("Download Report (Markdown)", md_report, file_name="meetmind_report.md", mime="text/markdown")
        
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"""
            <div class='meetmind-card'>
                <div class='card-title'>Card 1: Meeting Summary</div>
                <p style="color: #E3E3DE !important;">{res1.get('summary', '')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            conflicts_html = ""
            conflicts = res1.get('conflicts', [])
            if conflicts:
                conflicts_html = "<ul style='padding-left: 20px;'>" + "".join([f"<li style='color: #E3E3DE !important;'>{c}</li>" for c in conflicts]) + "</ul>"
            else:
                conflicts_html = "<p style='color: #E3E3DE !important;'>No major conflicts or open questions detected.</p>"
            st.markdown(f"""
            <div class='meetmind-card'>
                <div class='card-title'>Card 4: Unresolved Conflicts & Open Questions</div>
                {conflicts_html}
            </div>
            """, unsafe_allow_html=True)
            
            score = res3.get('overall_score', 0)
            color = "#22c55e" if score >= 8 else "#f59e0b" if score >= 5 else "#ef4444"
            c_score = res3.get('clarity_score', 0)
            d_score = res3.get('decisiveness_score', 0)
            a_score = res3.get('accountability_score', 0)
            st.markdown(f"""
            <div class='meetmind-card'>
                <div class='card-title'>Card 5: Meeting Health Score</div>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-top: 1.5rem; margin-bottom: 0.5rem;'>
                    <div style='text-align: center; flex: 1;'>
                        <h1 style='color: {color} !important; font-size: 3.5rem; margin: 0;'>{score}/10</h1>
                        <p style='color: #7D8C7C !important; font-size: 0.9rem; margin-top: 5px;'>{res3.get('one_line_verdict', '')}</p>
                    </div>
                    <div style='flex: 1.2; display: flex; flex-direction: column; gap: 1rem;'>
                        <div>
                            <div style='display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.4rem;'><span style='font-weight:600; color:#E3E3DE'>Clarity</span><span style='color:#E3E3DE'>{c_score}/10</span></div>
                            <div style='width: 100%; background-color: #0B100E; border-radius: 4px; height: 8px;'>
                                <div style='width: {min(100, max(0, c_score*10))}%; background-color: #7D8C7C; height: 100%; border-radius: 4px;'></div>
                            </div>
                        </div>
                        <div>
                            <div style='display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.4rem;'><span style='font-weight:600; color:#E3E3DE'>Decisiveness</span><span style='color:#E3E3DE'>{d_score}/10</span></div>
                            <div style='width: 100%; background-color: #0B100E; border-radius: 4px; height: 8px;'>
                                <div style='width: {min(100, max(0, d_score*10))}%; background-color: #7D8C7C; height: 100%; border-radius: 4px;'></div>
                            </div>
                        </div>
                        <div>
                            <div style='display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.4rem;'><span style='font-weight:600; color:#E3E3DE'>Accountability</span><span style='color:#E3E3DE'>{a_score}/10</span></div>
                            <div style='width: 100%; background-color: #0B100E; border-radius: 4px; height: 8px;'>
                                <div style='width: {min(100, max(0, a_score*10))}%; background-color: #7D8C7C; height: 100%; border-radius: 4px;'></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with c2:
            items = res1.get('action_items', [])
            table_html = ""
            if items:
                table_html = "<table class='custom-table'><tr><th>Task</th><th>Owner</th><th>Deadline</th><th>Priority</th></tr>"
                for item in items:
                    p = str(item.get('priority', 'Low'))
                    if 'high' in p.lower():
                        badge = f"<span class='badge badge-high'>High</span>"
                    elif 'medium' in p.lower():
                        badge = f"<span class='badge badge-medium'>Medium</span>"
                    else:
                        badge = f"<span class='badge badge-low'>Low</span>"
                    table_html += f"<tr><td>{item.get('task','')}</td><td>{item.get('owner','')}</td><td>{item.get('deadline','')}</td><td>{badge}</td></tr>"
                table_html += "</table>"
            else:
                table_html = "<p style='color: #E3E3DE !important;'>No action items assigned.</p>"
            st.markdown(f"""
            <div class='meetmind-card'>
                <div class='card-title'>Card 2: Action Items</div>
                {table_html}
            </div>
            """, unsafe_allow_html=True)
            
            emails = res2.get('emails', [])
            emails_html = ""
            if emails:
                for idx, email in enumerate(emails):
                    emails_html += f"""
                    <details style="background-color: #0B100E; border: 1px solid rgba(125, 140, 124, 0.15); border-radius: 6px; margin-bottom: 0.8rem; padding: 0.8rem;">
                        <summary style="cursor: pointer; color: #E3E3DE; font-weight: 500; font-size: 0.95rem; display: flex; align-items: center; gap: 8px;">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="Mm9 18l6-6-6-6"/></svg>
                            To: {email.get('owner', 'Team')} - {email.get('subject', 'Follow-up')}
                        </summary>
                        <textarea style="width: 100%; height: 180px; background-color: #1A1F1D; color: #E3E3DE; border: 1px solid rgba(125,140,124,0.2); border-radius: 6px; margin-top: 1rem; padding: 0.8rem; font-family: 'Inter', sans-serif; resize: vertical;">{email.get('body', '')}</textarea>
                    </details>
                    """
            else:
                emails_html = "<p style='color: #E3E3DE !important;'>No emails drafted.</p>"
            st.markdown(f"""
            <div class='meetmind-card'>
                <div class='card-title'>Card 3: Auto-Draft Follow-up Emails</div>
                {emails_html}
            </div>
            """, unsafe_allow_html=True)

def render_how_it_works():
    st.markdown("<h1 style='color: #E3E3DE; text-align: center; margin-top: 2rem;'>How MeetMind Works</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7D8C7C; font-size: 1.1rem; margin-bottom: 3rem;'>An advanced agentic pipeline processing your meetings seamlessly.</p>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("<div class='meetmind-card' style='text-align: center; height: 260px; display: flex; flex-direction: column; justify-content: center;'><h1 style='font-size: 2.5rem; margin-bottom: 10px; color:#E3E3DE'>📋</h1><h3 style='color: #E3E3DE; font-size: 1.15rem;'>1. Paste Transcript</h3><p style='color: #7D8C7C; font-size: 0.9rem;'>Drop raw notes or AI-generated transcript directly.</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='meetmind-card' style='text-align: center; height: 260px; display: flex; flex-direction: column; justify-content: center;'><h1 style='font-size: 2.5rem; margin-bottom: 10px; color:#E3E3DE'>🤖</h1><h3 style='color: #E3E3DE; font-size: 1.15rem;'>2. Agent Analyzes</h3><p style='color: #7D8C7C; font-size: 0.9rem;'>The Context Agent summarizes & extracts conflicts.</p></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='meetmind-card' style='text-align: center; height: 260px; display: flex; flex-direction: column; justify-content: center;'><h1 style='font-size: 2.5rem; margin-bottom: 10px; color:#E3E3DE'>⚡</h1><h3 style='color: #E3E3DE; font-size: 1.15rem;'>3. Actions Extracted</h3><p style='color: #7D8C7C; font-size: 0.9rem;'>Task Agent structures tasks, owners, and deadlines.</p></div>", unsafe_allow_html=True)
    with c4:
        st.markdown("<div class='meetmind-card' style='text-align: center; height: 260px; display: flex; flex-direction: column; justify-content: center;'><h1 style='font-size: 2.5rem; margin-bottom: 10px; color:#E3E3DE'>📧</h1><h3 style='color: #E3E3DE; font-size: 1.15rem;'>4. Emails Drafted</h3><p style='color: #7D8C7C; font-size: 0.9rem;'>Communication Agent drafts custom follow-ups.</p></div>", unsafe_allow_html=True)

def render_about():
    st.markdown("<h1 style='color: #E3E3DE; text-align: center; margin-top: 2rem;'>About MeetMind</h1>", unsafe_allow_html=True)
    st.markdown("""
        <div style='max-width: 800px; margin: 0 auto; line-height: 1.6;'>
            <div class='meetmind-card'>
                <h3 style='color: #E3E3DE;'>The Problem</h3>
                <p>Unproductive meetings cost businesses over $37 billion every year. The biggest leak? Follow-through. Valuable insights dissolve because tasks aren't tracked and emails aren't sent.</p>
                <h3 style='color: #E3E3DE; margin-top: 1.5rem;'>What MeetMind Does</h3>
                <p>MeetMind is an enterprise-grade AI Productivity Agent that listens to the outcome of your meetings and actually does the legwork. Instead of sending one massive prompt, it uses an <strong>Agentic Chain</strong>:</p>
                <ul style='color: #7D8C7C;'>
                    <li><strong>Agent 1</strong>: Understands context and summarizes.</li>
                    <li><strong>Agent 2</strong>: Structures precise action items and owners.</li>
                    <li><strong>Agent 3</strong>: Communicates and evaluates health.</li>
                </ul>
            </div>
        </div>
    """, unsafe_allow_html=True)

def main():
    inject_custom_css()
    render_navbar()
    
    params = st.query_params
    page = params.get("page", "Home")
    
    if page == "Home":
        render_home()
    elif page == "How It Works":
        render_how_it_works()
    elif page == "About":
        render_about()
        
    st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #7D8C7C; font-size: 0.875rem; margin-top: 3rem; border-top: 1px solid rgba(125, 140, 124, 0.2);">
            Built by Rohit Kumbhar · MeetMind © 2026
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
