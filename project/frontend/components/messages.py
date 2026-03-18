"""
frontend/components/messages.py
--------------------------------
Renders chat messages with law-reference cards.

FIXES:
  - View More / View Less uses JS inside HTML (no st.button rerun to top)
  - Clause text is truly clamped to 5 lines by default via CSS
  - Clicking "View full text" expands in place without scrolling to top
  - Streaming user bubble kept separate so input stays at bottom
"""

import streamlit as st


def render_message(msg: dict, msg_idx: int) -> None:
    role    = msg["role"]
    content = msg["content"]
    refs    = msg.get("references", [])
    if role == "user":
        _render_user(content)
    else:
        _render_assistant(content, refs, msg_idx)


def render_streaming_user(query: str) -> None:
    st.markdown(f"""
    <div class="msg-row user-row">
      <div class="av av-you">YOU</div>
      <div class="msg-body"><div class="bubble-user">{query}</div></div>
    </div>""", unsafe_allow_html=True)


def render_message_list(messages: list) -> None:
    if not messages:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:var(--text3)">
          <div style="font-size:2.8rem;margin-bottom:14px">💬</div>
          <div style="font-size:0.90rem">Type your first legal question below.</div>
        </div>""", unsafe_allow_html=True)
        return
    st.markdown('<div class="msgs-wrap">', unsafe_allow_html=True)
    for i, msg in enumerate(messages):
        render_message(msg, i)
    st.markdown('</div>', unsafe_allow_html=True)


# --- private ---

def _render_user(content: str) -> None:
    st.markdown(f"""
    <div class="msg-row user-row">
      <div class="av av-you">YOU</div>
      <div class="msg-body"><div class="bubble-user">{content}</div></div>
    </div>""", unsafe_allow_html=True)


def _render_assistant(content: str, refs: list, msg_idx: int) -> None:
    st.markdown(f"""
    <div class="msg-row">
      <div class="av av-lex">L</div>
      <div class="msg-body"><div class="bubble-lex">{content}</div></div>
    </div>""", unsafe_allow_html=True)

    if refs:
        _render_cite_chips(refs)
        _render_ref_expander(refs, msg_idx)


def _render_cite_chips(refs: list) -> None:
    chips = "".join(
        f'<span class="cite-chip"><span class="cite-dot"></span>'
        f'§{r.get("section_number","?")} · {r.get("act_name","")[:22]}</span>'
        for r in refs
    )
    st.markdown(f'<div class="cite-row">{chips}</div>', unsafe_allow_html=True)


def _render_ref_expander(refs: list, msg_idx: int) -> None:
    with st.expander(
        f"📋  {len(refs)} law section{'s' if len(refs)!=1 else ''} retrieved",
        expanded=False,
    ):
        for i, ref in enumerate(refs):
            if hasattr(ref, "__dict__"):
                ref = ref.__dict__
            _render_ref_card_js(ref, msg_idx, i)
            if i < len(refs) - 1:
                st.markdown('<hr style="margin:10px 0">', unsafe_allow_html=True)


def _render_ref_card_js(ref: dict, msg_idx: int, ref_idx: int) -> None:
    """
    Renders a ref card with pure-JS View More toggle.
    No st.button = no scroll-to-top on click.
    """
    score     = ref.get("relevance_score", 0)
    score_pct = min(100, max(5, int((score + 5) / 10 * 100)))
    clause    = ref.get("clause_text", "").replace("'", "&#39;").replace('"', "&quot;")
    card_id   = f"rc_{msg_idx}_{ref_idx}"
    text_id   = f"rt_{msg_idx}_{ref_idx}"
    btn_id    = f"rb_{msg_idx}_{ref_idx}"

    # Truncate preview to first 400 chars shown via CSS clamp
    has_more  = len(ref.get("clause_text", "")) > 380
    source    = ref.get("source_url", "")
    src_html  = (
        f'<a href="{source}" target="_blank" class="ref-src-link">↗ Official source</a>'
        if source else ""
    )

    more_btn = f"""
      <button id="{btn_id}" class="vm-js-btn" onclick="
        var t=document.getElementById('{text_id}');
        var b=document.getElementById('{btn_id}');
        if(t.classList.contains('clamped')){{
          t.classList.remove('clamped');
          b.textContent='▲ Show less';
        }}else{{
          t.classList.add('clamped');
          b.textContent='▼ View full text';
        }}
      ">▼ View full text</button>
    """ if has_more else ""

    st.markdown(f"""
    <div class="ref-card" id="{card_id}">
      <div class="ref-top">
        <div class="ref-act">{ref.get('act_name','')}</div>
        <div class="ref-sec">§ {ref.get('section_number','')}</div>
      </div>
      <div class="ref-title">{ref.get('section_title','')}</div>
      <div class="ref-domain">{ref.get('domain','').replace('_',' ').title()}</div>
      <div class="ref-bar-wrap">
        <div class="ref-bar-fill" style="width:{score_pct}%"></div>
      </div>
      <div class="ref-text clamped" id="{text_id}">{ref.get('clause_text','')}</div>
      {more_btn}
      {src_html}
    </div>
    """, unsafe_allow_html=True)