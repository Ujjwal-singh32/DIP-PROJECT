"""
frontend/components/streaming.py
──────────────────────────────────
Handles the streaming response from the RAG pipeline.
Shows user bubble → streams bot tokens → saves to chat store.
"""

import streamlit as st

from backend.chat_store import add_message, get_chat_history_for_llm
from frontend.components.messages import render_streaming_user


def run_stream(pipeline, query: str, chat_id: str) -> None:
    """
    Full streaming flow:
      1. Save user message
      2. Show user bubble immediately
      3. Stream bot tokens into a placeholder
      4. Save completed answer to chat store
      5. Bump form_key so the form resets on rerun
    """
    # Save user message
    add_message(chat_id, "user", query)

    # Build history (exclude the message we just added)
    history = get_chat_history_for_llm(chat_id)
    history = history[:-1] if history else []

    # Show user bubble right away
    render_streaming_user(query)

    # Placeholders
    stream_ph  = st.empty()
    status_ph  = st.status("🔍 Searching law sections…", expanded=False)

    streamed    = ""
    references  = []
    full_answer = ""

    for event in pipeline.stream_query(query, external_history=history):

        if event["type"] == "references":
            references = event["data"]
            n = len(references)
            status_ph.update(
                label=f"✓ {n} section{'s' if n!=1 else ''} found — writing answer…"
            )

        elif event["type"] == "chunk":
            streamed += event["text"]
            stream_ph.markdown(
                f'<div class="msg-row">'
                f'<div class="av av-lex">L</div>'
                f'<div class="msg-body">'
                f'<div class="bubble-lex">{streamed}<span class="cursor"></span></div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

        elif event["type"] == "done":
            full_answer = event["full_answer"]
            stream_ph.markdown(
                f'<div class="msg-row">'
                f'<div class="av av-lex">L</div>'
                f'<div class="msg-body">'
                f'<div class="bubble-lex">{full_answer}</div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
            status_ph.update(label="✓ Answer ready", state="complete")

        elif event["type"] == "error":
            full_answer = "Sorry, an error occurred. Please try again."
            stream_ph.error(f"Error: {event['message']}")
            status_ph.update(label="Error", state="error")

    # Persist completed answer
    if full_answer:
        add_message(chat_id, "assistant", full_answer, references=references)

    # Reset form so input clears and page doesn't scroll
    st.session_state.form_key += 1