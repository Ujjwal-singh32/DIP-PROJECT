"""
frontend/components/input_bar.py
---------------------------------
Centered pill, fixed at bottom.
"""

import streamlit as st


def render_input_bar() -> tuple[str, bool]:
    """Render fixed-bottom input. Returns (query, submitted)."""

    query     = ""
    submitted = False

    st.markdown('<div class="input-fixed"><div class="input-inner">', unsafe_allow_html=True)

    with st.form(key=f"chat_f{st.session_state.form_key}", clear_on_submit=True):
        cols = st.columns([1, 0.095])
        with cols[0]:
            query = st.text_input(
                label="q",
                placeholder="Ask about Indian law…",
                label_visibility="collapsed",
            )
        with cols[1]:
            submitted = st.form_submit_button("➤", use_container_width=True)

    st.markdown(
        '<div class="input-hint">'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown('</div></div>', unsafe_allow_html=True)

    return query or "", submitted