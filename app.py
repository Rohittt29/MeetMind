import os
from html import escape
from pathlib import Path
from uuid import uuid4

import httpx
import streamlit as st
from dotenv import load_dotenv
from google.genai.errors import APIError
from pydantic import ValidationError

from analysis import correct_action, extract_notes, markdown_report
from recovery import Recovery
from samples import SAMPLES, client_preview

load_dotenv()
st.set_page_config(page_title="MeetMind · Meeting recap", page_icon="📝", layout="centered")
state = st.session_state


def load_sample():
    if state.sample in SAMPLES:
        state.transcript = SAMPLES[state.sample]
        state.meeting_type = state.sample


def save_result(result):
    state.report = result
    state.report_input = (state.transcript.strip(), state.meeting_type)
    state.report_id = uuid4().hex


@st.dialog("Example recap", width="large")
def preview_sample():
    st.caption("Prepared example · Client call")
    if "example_report" not in state:
        state.example_report = client_preview()
    render_report(state.example_report, "example", SAMPLES["Client Call"])


@st.fragment(run_every=1)
def poll_sections(recovery):
    if recovery.collect():
        st.rerun()


def section_status(recovery, section):
    if recovery is None:
        return
    if section in recovery.jobs:
        st.caption("Generating this section… Your action items are ready to review and download.")
    elif section in recovery.failed:
        st.warning("This section could not be generated. Your completed work is available.")
        label = "Retry follow-up emails" if section == "emails" else "Retry meeting quality"
        if st.button(label):
            recovery.start(section, os.getenv("GEMINI_API_KEY"), os.getenv("GEMINI_MODEL", "gemini-flash-latest"))
            st.rerun()


def render_report(report, report_id, transcript, recovery=None):
    notes, drafts, quality = report
    st.text(notes.summary)
    actions, followups, review = st.tabs(["Action items", "Follow-up emails", "Meeting quality"])
    with actions:
        for index, item in enumerate(notes.action_items):
            with st.container(border=True):
                header = st.empty()
                quote = getattr(item, "source_quote", "")
                if quote and quote in transcript:
                    start = transcript.index(quote)
                    with st.expander("View transcript evidence"):
                        before = transcript[max(0, start - 120):start]
                        end = start + len(quote)
                        after = transcript[end:end + 120]
                        st.html(f"<p>{escape(before)}<mark>{escape(quote)}</mark>{escape(after)}</p>")
                else:
                    st.caption("No exact transcript excerpt available.")
                with st.expander("Edit action item"):
                    with st.form(f"{report_id}_action_{index}"):
                        task = st.text_input("Task", item.task, key=f"{report_id}_{index}_task")
                        owner = st.text_input("Owner", item.owner, key=f"{report_id}_{index}_owner")
                        deadline = st.text_input("Deadline", item.deadline, key=f"{report_id}_{index}_deadline")
                        st.caption("Saving a correction rewrites follow-up drafts for the affected owners.")
                        if st.form_submit_button("Save correction"):
                            try:
                                affected = correct_action(notes, drafts, index, task, owner, deadline)
                            except ValueError as error:
                                st.error(str(error))
                            else:
                                if recovery is not None:
                                    recovery.corrected_owners.update(affected)
                                for name in affected:
                                    state[f"{report_id}_rev_{name}"] = uuid4().hex
                                st.success("Action item saved.")
                header.html(
                    f'<p class="task-name">{escape(item.task)}</p><div class="task-meta">'
                    f'<span>Owner · {escape(item.owner)}</span><span>Due · {escape(item.deadline)}</span>'
                    f'<span>Priority · {escape(item.priority)}</span></div>'
                )
        if not notes.action_items:
            st.caption("No commitments identified.")
        st.subheader("Open questions")
        for question in notes.conflicts:
            st.text("• " + question)
        if not notes.conflicts:
            st.caption("No open questions identified.")
    with followups:
        section_status(recovery, "emails")
        if not drafts.emails and (recovery is None or "emails" not in recovery.missing):
            st.caption("No owner-specific follow-ups to draft.")
        for idx, email in enumerate(drafts.emails):
            with st.container(border=True):
                st.text(f"To {email.owner}")
                revision = state.get(f"{report_id}_rev_{email.owner}", "initial")
                prefix = f"{report_id}_{email.owner}_{revision}_{idx}"
                email.subject = st.text_input("Subject", email.subject, key=prefix + "_subject")
                email.body = st.text_area("Message", email.body, height=160, key=prefix + "_body")
    with review:
        section_status(recovery, "quality")
        if quality is not None:
            st.metric("Overall meeting quality", f"{quality.overall:g} / 10")
            st.text(quality.verdict)
            for label in ("clarity", "decisiveness", "accountability"):
                value = getattr(quality, label)
                st.progress(value / 10, text=f"{label.title()}  ·  {value:g}/10")
    st.download_button("Download recap (.md)", markdown_report(notes, drafts, quality, missing=recovery.missing if recovery else ()),
                       file_name="meetmind-recap.md", mime="text/markdown", key=f"download_{report_id}", on_click="ignore")


def workspace():
    heights = [18, 28, 47, 32, 55, 76, 91, 64, 47, 31, 45, 70, 84, 60, 42, 25, 36, 52, 67, 48, 29, 19]
    bars = "".join(f'<i style="height:{h}%"></i>' for h in heights)
    st.html(
        f'<section class="studio-cover"><div class="sound" aria-hidden="true">{bars}</div>'
        '<h1>Your meeting, recapped.</h1>'
        '<p>Turn the conversation into clear action items, deadlines, and follow-up drafts.</p></section>'
    )
    composer, example = st.columns([1.8, 1], gap="medium")
    with composer.container(key="composer"):
        st.header("Create a recap")
        transcript = st.text_area("Meeting transcript", key="transcript", height=148,
                                  placeholder="Paste your meeting notes or transcript here…")
        left, right = st.columns(2)
        left.selectbox("Meeting type", [*SAMPLES, "1-on-1"], key="meeting_type")
        right.selectbox("Load sample transcript", ["Choose a sample", *SAMPLES], key="sample", on_change=load_sample)
        run = st.button("Create recap", type="primary", icon=":material/auto_awesome:", disabled=not transcript.strip())
        st.caption("Creating a recap sends the transcript to Google Gemini.")
    with example.container(key="example"):
        st.header("Inside a sample recap")
        st.html('<blockquote>“John will handle the basic PDF export by Friday.”</blockquote>'
                '<p class="sample-source">From the client call sample</p>')
        st.write("See the action item and follow-up email drawn from this conversation.")
        if st.button("Explore sample recap", icon=":material/arrow_outward:"):
            preview_sample()
    if run:
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            st.warning("Live analysis needs a Gemini key. Try the sample recap, or set GEMINI_API_KEY in the app environment or Streamlit secrets.")
        else:
            with st.status("Creating recap…") as status:
                try:
                    model = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
                    notes = extract_notes(transcript, state.meeting_type, key, model)
                except (APIError, httpx.HTTPError, ValidationError) as error:
                    status.update(label="Couldn’t create this recap", state="error")
                    code = getattr(error, "code", None)
                    if code == 429:
                        st.error("Gemini’s quota or rate limit was reached. Check the quota and try again later.")
                    elif code in (400, 401, 403, 404):
                        st.error("Gemini rejected the request. Check the configured model, API key, and transcript length.")
                    else:
                        st.error("The response was incomplete or the service was unavailable. Try again.")
                else:
                    recovery = Recovery(notes, transcript)
                    save_result((notes, recovery.drafts, None))
                    state.recovery = recovery
                    for section in ("emails", "quality"):
                        recovery.start(section, key, model)
                    status.update(label="Action items ready", state="complete", expanded=False)
    if "report" in state:
        if state.report_input == (transcript.strip(), state.meeting_type):
            st.header("Meeting recap")
            recovery = state.get("recovery")
            if recovery is not None:
                recovery.collect()
                state.report = (recovery.notes, recovery.drafts, recovery.quality)
            render_report(state.report, state.report_id, state.report_input[0], recovery)
            if recovery is not None and recovery.jobs:
                poll_sections(recovery)
        else:
            st.info("The meeting input has changed. Create a recap for this version.")


st.html(Path(__file__).with_name("studio.css"))
with st.container(key="masthead"):
    brand, shortcut = st.columns([3, 2])
    brand.html('<div class="studio-brand"><span aria-hidden="true" class="brand-mark">'
               '<i style="height:9px"></i><i style="height:19px"></i><i style="height:13px"></i>'
               '</span>MeetMind</div>')
    if shortcut.button("View example", key="mobile_example"):
        preview_sample()
page = st.query_params.get("page", "Home")
if page in ("How It Works", "About"):
    st.title(page)
    st.write("MeetMind extracts commitments, drafts follow-ups for named owners, and reviews meeting quality. "
             "Review the recap and edit email drafts before downloading. You choose what to share.")
    if st.button("Open workspace"):
        st.query_params.clear()
        st.rerun()
else:
    workspace()
    with st.expander("How MeetMind works"):
        st.write("Paste speaker-labelled notes, choose a meeting type, and create a recap. "
                 "Review commitments and open questions, edit each email draft, then download the Markdown report.")
