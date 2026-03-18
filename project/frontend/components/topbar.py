"""
frontend/components/topbar.py
──────────────────────────────
"""

import streamlit as st


def render_topbar(active_chat: dict | None = None) -> None:
    if active_chat:
        st.markdown(f"""
        <div class="top-bar">
          <div class="tb-logo">
            <div class="tb-icon">✦</div>
            <div class="tb-name">LexAI</div>
          </div>
          <div class="tb-chat-pill">
            <span class="tb-chat-dot"></span>
            <span class="tb-chat-title">{active_chat['title']}</span>
            <span class="tb-chat-id">#{active_chat['chat_id']}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="top-bar">
          <div class="tb-logo">
            <div class="tb-icon">✦</div>
            <div class="tb-name">LexAI</div>
          </div>
          <div class="tb-model-badge">
            <span class="tb-model-dot"></span>
            Indian Legal RAG Agent
          </div>
        </div>
        """, unsafe_allow_html=True)