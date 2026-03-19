"""
frontend/streamlit_app.py
──────────────────────────
LexAI main entry point.

This file is intentionally lean — it only:
  1. Configures Streamlit
  2. Loads the RAG pipeline
  3. Manages session state
  4. Calls modular components

All UI lives in frontend/components/:
  styles.py    — CSS design tokens
  sidebar.py   — conversation history panel
  topbar.py    — sticky header
  welcome.py   — empty state
  messages.py  — chat bubbles + law-reference cards
  input_bar.py — search input
  streaming.py — token streaming + chat persistence
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LexAI — Indian Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Components ────────────────────────────────────────────────────────────────
from frontend.components import (
    inject_css,
    render_sidebar,
    render_topbar,
    render_welcome,
    render_message_list,
    render_input_bar,
    run_stream,
)
from backend.chat_store import create_chat, load_chat


# ── Pipeline (cached across reruns) ──────────────────────────────────────────
@st.cache_resource(show_spinner="Loading LexAI…")
def get_pipeline():
    from backend.rag_pipeline import RAGPipeline
    return RAGPipeline()


# ── Session state defaults ────────────────────────────────────────────────────
def _init_state() -> None:
    defaults = {
        "active_chat_id": None,
        "expanded_refs":  {},
        "form_key":       0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    _init_state()
    inject_css()

    # Load pipeline
    pipeline = None
    pipeline_error = None
    try:
        pipeline = get_pipeline()
    except Exception as exc:
        pipeline_error = str(exc)

    # Sidebar (always visible)
    render_sidebar(pipeline)

    # Pipeline error banner
    if pipeline_error:
        st.error(
            f"**Pipeline not ready:** {pipeline_error}\n\n"
            "Run `python scripts/build_vector_index.py` then restart the app."
        )
        st.stop()

    # Resolve active chat
    active_id   = st.session_state.active_chat_id
    active_chat = load_chat(active_id) if active_id else None

    # Top bar
    render_topbar(active_chat)

    # Messages area
    if not active_chat:
        render_welcome()
    else:
        render_message_list(active_chat.get("messages", []))

    # Keep live streaming output inside chat area (above the fixed input bar)
    live_container = st.container()

    # Input bar (always at bottom)
    query, submitted = render_input_bar()

    # Process query
    if submitted and query.strip():
        q = query.strip()

        # Create new chat session if none is active
        if not st.session_state.active_chat_id:
            chat = create_chat(first_message=q)
            st.session_state.active_chat_id = chat["chat_id"]

        # Stream response, save to disk, bump form_key
        run_stream(pipeline, q, st.session_state.active_chat_id, live_container=live_container)

        # Rerun to render the saved message from disk
        st.rerun()


if __name__ == "__main__":
    main()