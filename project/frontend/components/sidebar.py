"""
frontend/components/sidebar.py
───────────────────────────────
Sidebar: brand, new-chat button, conversation history, footer.
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
        # ── Brand ─────────────────────────────────────────────────────────
        st.markdown("""
        <div class="sb-brand">
          <div class="sb-logo"><b>Lex</b><span>AI</span></div>
          <div class="sb-tagline">Indian Legal Intelligence</div>
        </div>
        """, unsafe_allow_html=True)

        # ── New chat ───────────────────────────────────────────────────────
        st.markdown('<div class="sb-newchat">', unsafe_allow_html=True)
        if st.button("＋  New conversation", use_container_width=True, key="btn_new"):
            st.session_state.active_chat_id = None
            st.session_state.expanded_refs  = {}
            st.session_state.form_key      += 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # ── History ────────────────────────────────────────────────────────
        st.markdown('<hr>', unsafe_allow_html=True)
        all_chats = list_chats()

        if all_chats:
            st.markdown('<div class="sb-section">Recent</div>', unsafe_allow_html=True)
            for chat in all_chats:
                _render_chat_item(chat)
        else:
            st.markdown(
                '<div style="padding:12px 18px;font-size:0.78rem;color:var(--text3)">'
                'No conversations yet.</div>',
                unsafe_allow_html=True,
            )

        # ── Footer ─────────────────────────────────────────────────────────
        idx = pipeline.vector_store.total_vectors if pipeline else 0
        st.markdown(f"""
        <div class="sb-footer">
          <div class="sb-stat">
            <span class="sb-dot"></span>
            {idx:,} law sections indexed
          </div>
          ⚠ General information only.<br>
          Consult a qualified advocate for legal advice.
        </div>
        """, unsafe_allow_html=True)


def _render_chat_item(chat: dict) -> None:
    cid       = chat["chat_id"]
    is_active = (cid == st.session_state.get("active_chat_id"))
    ac        = "active" if is_active else ""

    st.markdown(f"""
    <div class="ch-item {ac}">
      <div class="ch-title">{chat['title']}</div>
      <div class="ch-meta">
        <span class="ch-badge">#{cid}</span>
        <span>{chat['message_count']} msgs</span>
        <span>{_fmt_time(chat['updated_at'])}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown('<div class="ch-open-btn">', unsafe_allow_html=True)
        if st.button("Open", key=f"open_{cid}", use_container_width=True):
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