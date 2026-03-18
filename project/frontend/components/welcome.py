"""
frontend/components/welcome.py
───────────────────────────────
"""

import streamlit as st


def render_welcome() -> None:
    st.markdown("""
    <div class="welcome-wrap">

      <div class="welcome-greeting">
        Hello, <span class="grad-text">legal researcher.</span>
      </div>
      <div class="welcome-subtitle">
        How can I help you today?
      </div>

      <div class="suggestion-grid">
        <div class="suggestion-card">
          <div class="suggestion-icon">🔍</div>
          <div class="suggestion-title">Look up a specific section</div>
          <div class="suggestion-desc">Find exact clause text from any Indian statute or act</div>
        </div>
        <div class="suggestion-card">
          <div class="suggestion-icon">⚖️</div>
          <div class="suggestion-title">Understand criminal law</div>
          <div class="suggestion-desc">Explain offences under BNS 2023, IPC, CrPC with penalties</div>
        </div>
        <div class="suggestion-card">
          <div class="suggestion-icon">💻</div>
          <div class="suggestion-title">Cyber law & IT Act</div>
          <div class="suggestion-desc">Data protection, cyber offences, and digital evidence rules</div>
        </div>
        <div class="suggestion-card">
          <div class="suggestion-icon">🛡️</div>
          <div class="suggestion-title">Consumer &amp; contract rights</div>
          <div class="suggestion-desc">Remedies, disputes, and your rights under Indian civil law</div>
        </div>
      </div>

    </div>
    """, unsafe_allow_html=True)