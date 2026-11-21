import os
from uuid import uuid4

import httpx
import streamlit as st
from dotenv import load_dotenv
from google.genai.errors import APIError
from pydantic import ValidationError

from analysis import analyze, markdown_report
from samples import SAMPLES, client_preview

load_dotenv()
st.set_page_config(page_title="MeetMind · Meeting recap", page_icon="📝", layout="centered")
state = st.session_state


def load_sample():
    if state.sample in SAMPLES:
        state.transcript = SAMPLES[state.sample]
        state.meeting_type = state.sample


def save_result(result, preview=False):
    state.report = result
    state.report_input = (state.transcript.strip(), state.meeting_type)
    state.report_id = uuid4().hex
    state.preview = preview


def preview_sample():
    state.sample = "Client Call"
    load_sample()
    save_result(client_preview(), preview=True)


def render_report():
    notes, drafts, quality = state.report
    st.divider()
    st.header("Meeting recap")
    if state.preview:
        st.caption("Example recap · Prepared from the client call sample")
    st.text(notes.summary)
    actions, followups, review = st.tabs(["Action items", "Follow-up emails", "Meeting quality"])
    with actions:
        for item in notes.action_items:
            with st.container(border=True):
                st.text(item.task)
                st.text(f"Owner: {item.owner}   ·   Due: {item.deadline}   ·   Priority: {item.priority}")
        if not notes.action_items:
            st.caption("No commitments identified.")
        st.subheader("Open questions")
        for question in notes.conflicts:
            st.text("• " + question)
        if not notes.conflicts:
            st.caption("No open questions identified.")
    with followups:
        if not drafts.emails:
            st.caption("No owner-specific follow-ups to draft.")
        for idx, email in enumerate(drafts.emails):
            with st.container(border=True):
                st.text(f"To {email.owner}")
                prefix = f"{state.report_id}_{idx}"
                email.subject = st.text_input("Subject", email.subject, key=prefix + "_subject")
                email.body = st.text_area("Message", email.body, height=160, key=prefix + "_body")
    with review:
        st.metric("Overall meeting quality", f"{quality.overall:g} / 10")
        st.text(quality.verdict)
        for label in ("clarity", "decisiveness", "accountability"):
            value = getattr(quality, label)
            st.progress(value / 10, text=f"{label.title()}  ·  {value:g}/10")
    st.download_button("Download recap (.md)", markdown_report(notes, drafts, quality),
                       file_name="meetmind-recap.md", mime="text/markdown")


def workspace():
    st.title("Meeting workspace")
    st.write("Turn a transcript into a recap with owners, deadlines, and follow-up emails.")
    with st.container(border=True):
        st.subheader("Meeting transcript")
        left, right = st.columns(2)
        left.selectbox("Meeting type", [*SAMPLES, "1-on-1"], key="meeting_type")
        right.selectbox("Load sample transcript", ["Choose a sample", *SAMPLES], key="sample", on_change=load_sample)
        transcript = st.text_area("Transcript", key="transcript", height=200,
                                  placeholder="Paste the conversation here, including speaker names if available.")
        st.caption("Creating a recap sends this transcript to Google Gemini.")
        run = st.button("Create recap", type="primary", disabled=not transcript.strip())
        st.button("Preview a sample recap", on_click=preview_sample, help="Open a prepared client call example without an API key.")
    if run:
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            st.warning("Live analysis needs a Gemini key. Try the sample recap, or set GEMINI_API_KEY in the app environment or Streamlit secrets.")
        else:
            with st.status("Creating recap…") as status:
                try:
                    result = analyze(transcript, state.meeting_type, key, os.getenv("GEMINI_MODEL", "gemini-flash-latest"), status.write)
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
                    save_result(result)
                    status.update(label="Recap ready", state="complete", expanded=False)
    if "report" in state:
        if state.report_input == (transcript.strip(), state.meeting_type):
            render_report()
        else:
            st.info("The meeting input has changed. Create a recap for this version.")


st.markdown("**◈　MeetMind**")
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
