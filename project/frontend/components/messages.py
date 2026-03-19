"""
frontend/components/messages.py
--------------------------------
User: right-aligned pill.
"""

import html
import re
from urllib.parse import quote

import streamlit as st


def _clean_ref_text(raw: str) -> str:
    """Strip accidental HTML fragments from law text before rendering."""
    text = html.unescape(str(raw or ""))
    text = re.sub(r"(?is)<script.*?>.*?</script>", "", text)
    text = re.sub(r"(?is)<style.*?>.*?</style>", "", text)
    text = re.sub(r"(?is)<[^>]+>", "", text)
    text = re.sub(r"(?i)</?\s*div\s*>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def render_message(msg: dict, msg_idx: int) -> None:
    role    = msg["role"]
    content = msg["content"]
    refs    = msg.get("references", [])
    if role == "user":
        _render_user(content)
    else:
        _render_assistant(content, refs, msg_idx)


def render_streaming_user(query: str) -> None:
    escaped = html.escape(str(query))
    st.markdown(f"""
    <div class="msg-row user-row">
      <div class="av av-you">U</div>
      <div class="msg-body"><div class="bubble-user">{escaped}</div></div>
    </div>""", unsafe_allow_html=True)


def render_message_list(messages: list) -> None:
    if not messages:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:var(--on-surface-3)">
          <div style="font-size:2.5rem;margin-bottom:12px">💬</div>
          <div style="font-size:0.9375rem">Type your first legal question below.</div>
        </div>""", unsafe_allow_html=True)
        return
    st.markdown('<div class="msgs-wrap">', unsafe_allow_html=True)
    for i, msg in enumerate(messages):
        render_message(msg, i)
    st.markdown('</div>', unsafe_allow_html=True)


# --- private ---

def _render_user(content: str) -> None:
    escaped = html.escape(str(content))
    st.markdown(f"""
    <div class="msg-row user-row">
      <div class="av av-you">U</div>
      <div class="msg-body"><div class="bubble-user">{escaped}</div></div>
    </div>""", unsafe_allow_html=True)


def _render_assistant(content: str, refs: list, msg_idx: int) -> None:
    rendered_content = _render_assistant_content_block(content)
    st.markdown(f"""
    <div class="msg-row">
      <div class="av av-lex">✦</div>
      <div class="msg-body"><div class="bubble-lex">{rendered_content}</div></div>
    </div>""", unsafe_allow_html=True)

    if refs:
        _render_cite_chips(refs)
        _render_ref_expander(refs, msg_idx)


def _render_assistant_content_block(content: str) -> str:
    """Parse tagged LLM answer into summary + details dropdown UI."""
    text = str(content or "").strip()

    act_match = re.search(r"\[ACT_SECTION\]\s*(.+)", text)
    brief_match = re.search(r"\[BRIEF\]\s*(.+)", text)
    detailed_match = re.search(r"\[DETAILED\]\s*([\s\S]+)$", text)

    # Fallback for any legacy/unstructured response
    if not (act_match and brief_match and detailed_match):
        fallback = html.escape(text).replace("\n", "<br>")
        return fallback

    act_line = html.escape(act_match.group(1).strip())
    brief_line = html.escape(brief_match.group(1).strip()).replace("\n", "<br>")
    detailed_text = html.escape(detailed_match.group(1).strip()).replace("\n", "<br>")

    return f"""
    <div class="ans-compact">
      <div class="ans-act">{act_line}</div>
      <div class="ans-brief">{brief_line}</div>
      <details class="ans-details">
        <summary class="ans-details-btn">
          <span class="ans-open">▼ View detailed description</span>
          <span class="ans-close">▲ Hide detailed description</span>
        </summary>
        <div class="ans-detailed">{detailed_text}</div>
      </details>
    </div>
    """


def _render_cite_chips(refs: list) -> None:
    chips = "".join(
        f'<span class="cite-chip"><span class="cite-dot"></span>'
    f'{html.escape(str(r.get("section_number","?")))} · {html.escape(str(r.get("act_name","")))}</span>'
        for r in refs
    )
    st.markdown(f'<div class="cite-row">{chips}</div>', unsafe_allow_html=True)


def _render_ref_expander(refs: list, msg_idx: int) -> None:
    n = len(refs)
    label = f"📋  {n} law section{'s' if n != 1 else ''} retrieved"
    with st.expander(label, expanded=False):
        for i, ref in enumerate(refs):
            if hasattr(ref, "__dict__"):
                ref = ref.__dict__
            _render_ref_card_js(ref, msg_idx, i)
            if i < len(refs) - 1:
                st.markdown('<hr style="margin:10px 0">', unsafe_allow_html=True)


def _render_ref_card_js(ref: dict, msg_idx: int, ref_idx: int) -> None:
    """Ref card with native details/summary toggle for stable expand/collapse."""
    score        = ref.get("relevance_score", 0)
    score_pct    = min(100, max(5, int((score + 5) / 10 * 100)))
    act_name     = str(ref.get("act_name", ""))
    sec_num      = str(ref.get("section_number", ""))
    sec_title    = str(ref.get("section_title", ""))
    domain       = str(ref.get("domain", "")).replace("_", " ").title()
    clause_text  = _clean_ref_text(ref.get("clause_text", ""))

    esc_act      = html.escape(act_name)
    esc_sec      = html.escape(sec_num)
    esc_title    = html.escape(sec_title)
    esc_domain   = html.escape(domain)
    esc_clause   = html.escape(clause_text)
    
    # Aggressive stripping of any leftover stray escaped div tags that bypass regex
    esc_clause = re.sub(r"(?i)&lt;/?.*?div.*?&gt;", "", esc_clause).strip()
    
    # CRITICAL: Streamlit's Markdown parser breaks HTML blocks if they contain double newlines.
    # We replace \n with <br> to ensure the text renders inside the div as a continuous HTML block,
    # preventing the template's actual closing </div> from being treated as an isolated plain text paragraph.
    esc_clause = esc_clause.replace("\n", "<br>")

    copy_payload = f"{act_name}\nSection {sec_num}: {sec_title}\n\n{clause_text}"
    copy_q       = quote(copy_payload)

    card_id  = f"rc_{msg_idx}_{ref_idx}"

    has_more    = len(clause_text) > 380
    source      = str(ref.get("source_url", ""))
    safe_source = html.escape(source, quote=True)
    src_html    = (
        f'<a href="{safe_source}" target="_blank" class="ref-src-link">↗ Official source</a>'
        if source.startswith("http") else ""
    )

    text_block = (
        f"""
      <details class="ref-more">
        <summary class="vm-js-btn">
          <span class="vm-open">▼ View full text</span>
          <span class="vm-close">▲ Show less</span>
        </summary>
        <div class="ref-text ref-text-full">{esc_clause}</div>
      </details>
      <div class="ref-text ref-text-preview clamped">{esc_clause}</div>
        """
        if has_more
        else f'<div class="ref-text">{esc_clause}</div>'
    )

    st.markdown(f"""
    <div class="ref-card" id="{card_id}">
      <div class="ref-top">
        <div class="ref-act">{esc_act}</div>
        <div class="ref-right">
          <button class="ref-copy-btn" title="Copy section"
            data-copy="{copy_q}"
            onclick="(function(btn){{
              var text=decodeURIComponent(btn.getAttribute('data-copy')||'');
              function setState(ok){{
                var prev=btn.textContent;btn.textContent=ok?'Copied':'Failed';
                setTimeout(function(){{btn.textContent=prev;}},2000);
              }}
              function fallback(){{
                var ta=document.createElement('textarea');ta.value=text;
                ta.style.position='absolute';ta.style.left='-9999px';
                document.body.appendChild(ta);ta.select();
                try{{document.execCommand('copy');setState(true);}}
                catch(e){{setState(false);}}
                document.body.removeChild(ta);
              }}
              if(navigator.clipboard&&window.isSecureContext){{
                navigator.clipboard.writeText(text).then(function(){{setState(true);}}).catch(fallback);
              }}else{{fallback();}}
            }})(this);">Copy</button>
          <div class="ref-sec">{esc_sec}</div>
        </div>
      </div>
      <div class="ref-title">{esc_title}</div>
      <div class="ref-domain">{esc_domain}</div>
      <div class="ref-bar-wrap">
        <div class="ref-bar-fill" style="width:{score_pct}%"></div>
      </div>
      {text_block}
      {src_html}
    </div>
    """, unsafe_allow_html=True)