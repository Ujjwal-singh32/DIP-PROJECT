"""
frontend/components/sidebar.py

"""

import streamlit as st
from backend.chat_store import list_chats, delete_chat


def _fmt_time(iso: str) -> str:
    try:
        from datetime import datetime
        return datetime.fromisoformat(iso).strftime("%b %d")
    except Exception:
        return ""


def render_sidebar(pipeline=None) -> None:
    with st.sidebar:
        # ── Header ────────────────────────────────────────────────────────
        st.markdown("""
        <div class="sb-header">
          <div class="sb-app-name">LexAI</div>
        </div>
        """, unsafe_allow_html=True)

        # ── New Chat ───────────────────────────────────────────────────────
        st.markdown('<div class="sb-newchat">', unsafe_allow_html=True)
        if st.button("✏  New chat", use_container_width=True, key="btn_new"):
            st.session_state.active_chat_id = None
            st.session_state.expanded_refs  = {}
            st.session_state.form_key      += 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Conversation History ───────────────────────────────────────────
        st.markdown('<hr>', unsafe_allow_html=True)
        all_chats = list_chats()

        if all_chats:
            st.markdown('<div class="sb-section-label">Recent</div>', unsafe_allow_html=True)
            for chat in all_chats:
                _render_chat_item(chat)
        else:
            st.markdown(
                '<div style="padding:10px 16px;font-size:0.8125rem;color:var(--on-surface-3)">'
                'No conversations yet.</div>',
                unsafe_allow_html=True,
            )

        # ── Footer ─────────────────────────────────────────────────────────
        idx = pipeline.vector_store.total_vectors if pipeline else 0
        st.markdown(f"""
        <div class="sb-footer">
          <div class="sb-stat">
            <span class="sb-dot"></span>
            {idx:,} sections indexed
          </div>
          ⚠ General information only. Consult an advocate for legal advice.
        </div>
        """, unsafe_allow_html=True)


def _render_chat_item(chat: dict) -> None:
    cid       = chat["chat_id"]
    is_active = (cid == st.session_state.get("active_chat_id"))
    ac        = "active" if is_active else ""

    c1, c2 = st.columns([8, 1], gap="small")
    with c1:
        st.markdown(f'<div class="ch-row {ac}">', unsafe_allow_html=True)
        if st.button(chat["title"], key=f"open_{cid}", use_container_width=True):
            st.session_state.active_chat_id = cid
            st.session_state.expanded_refs  = {}
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="ch-del-btn">', unsafe_allow_html=True)
        if st.button("✕", key=f"del_{cid}"):
            delete_chat(cid)
            if st.session_state.get("active_chat_id") == cid:
                st.session_state.active_chat_id = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)