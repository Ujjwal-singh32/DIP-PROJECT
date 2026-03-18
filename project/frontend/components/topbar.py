"""
frontend/components/topbar.py
──────────────────────────────
Sticky top bar: logo + active chat title/ID pill.
"""

import streamlit as st


def render_topbar(active_chat: dict | None = None) -> None:
    if active_chat:
        st.markdown(f"""
        <div class="top-bar">
          <div class="tb-logo">
            <div class="tb-icon">⚖</div>
            <div class="tb-name">Lex<em>AI</em></div>
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
            <div class="tb-icon">⚖</div>
            <div class="tb-name">Lex<em>AI</em></div>
          </div>
          <div style="font-size:0.74rem;color:var(--text3);font-family:'JetBrains Mono',monospace;
               background:var(--bg3);border:1px solid var(--border2);border-radius:20px;
               padding:5px 14px;">
            Indian Legal Intelligence System
          </div>
        </div>
        """, unsafe_allow_html=True)