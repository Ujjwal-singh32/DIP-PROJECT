"""
frontend/components/input_bar.py
---------------------------------
Chat input bar — always fixed at the bottom of the viewport.
Input + Send button are on the exact same baseline (48px height each).

FIXES:
  - position:fixed keeps it pinned during streaming (no jump to top)
  - Input and button vertically aligned via flex + matching height CSS
  - Page content gets a bottom spacer so it isn't hidden behind the bar
"""

import streamlit as st


def render_input_bar() -> tuple[str, bool]:
    """Render fixed-bottom input. Returns (query, submitted)."""

    # Spacer prevents content being hidden under the fixed bar
    st.markdown('<div style="height:96px"></div>', unsafe_allow_html=True)

    query     = ""
    submitted = False

    st.markdown('<div class="input-fixed"><div class="input-inner">', unsafe_allow_html=True)

    with st.form(key=f"chat_f{st.session_state.form_key}", clear_on_submit=True):
        cols = st.columns([1, 0.13])
        with cols[0]:
            query = st.text_input(
                label="q",
                placeholder="Ask a legal question…  e.g. What is the punishment for theft under BNS 2023?",
                label_visibility="collapsed",
            )
        with cols[1]:
            submitted = st.form_submit_button("Send →", use_container_width=True)

    st.markdown(
        '<div class="input-hint">Enter or Send &middot; LexAI cites exact Act &amp; Section</div>',
        unsafe_allow_html=True,
    )
    st.markdown('</div></div>', unsafe_allow_html=True)

    return query or "", submitted