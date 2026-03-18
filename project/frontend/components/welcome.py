"""
frontend/components/welcome.py
───────────────────────────────
Welcome / empty state shown when no chat is active.
"""

import streamlit as st


def render_welcome() -> None:
    st.markdown("""
    <div class="welcome-wrap">
      <div class="welcome-seal">⚖️</div>
      <div class="welcome-h">Ask anything about <span>Indian Law</span></div>
      <div class="welcome-p">
        LexAI retrieves the exact section, act name, and clause text from
        Indian statutes — and cites every source in the answer.
        Ask about criminal law, contracts, cyber offences, consumer rights, and more.
      </div>
      <div class="feat-pills">
        <span class="feat-pill"><span class="fp-dot"></span>Exact section citations</span>
        <span class="feat-pill"><span class="fp-dot"></span>BNS · IPC · IT Act · ICA</span>
        <span class="feat-pill"><span class="fp-dot"></span>Conversation memory</span>
        <span class="feat-pill"><span class="fp-dot"></span>Full clause text on demand</span>
      </div>
    </div>
    """, unsafe_allow_html=True)