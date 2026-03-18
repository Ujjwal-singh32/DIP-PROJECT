"""
frontend/components/styles.py
─────────────────────────────
Single source of truth for all CSS.
Change PALETTE dict to retheme the entire app instantly.
Call inject_css() once at app startup.
"""

import streamlit as st

PALETTE = {
    "bg":       "#0c0f1a",
    "bg2":      "#131929",
    "bg3":      "#1a2236",
    "bg4":      "#212b40",
    "bg5":      "#273148",
    "gold":     "#e8b84b",
    "gold2":    "#f5d07a",
    "gold_bg":  "rgba(232,184,75,0.09)",
    "gold_bg2": "rgba(232,184,75,0.17)",
    "crimson":  "#e85c72",
    "green":    "#3ecf8e",
    "blue":     "#5b8dee",
    "text":     "#dce6f5",
    "text2":    "#8fa3c0",
    "text3":    "#4d647f",
    "border":   "#1e2d42",
    "border2":  "#27394f",
    "border3":  "#30465e",
}

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=Lora:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap');

:root{{
  --bg:{bg};--bg2:{bg2};--bg3:{bg3};--bg4:{bg4};--bg5:{bg5};
  --gold:{gold};--gold2:{gold2};--gold-bg:{gold_bg};--gold-bg2:{gold_bg2};
  --crimson:{crimson};--green:{green};--blue:{blue};
  --text:{text};--text2:{text2};--text3:{text3};
  --border:{border};--border2:{border2};--border3:{border3};
  --r:10px;--r-sm:7px;--r-lg:14px;
}}

*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
html,body,[class*="css"]{{font-family:'Sora',-apple-system,sans-serif!important;background:var(--bg)!important;color:var(--text)!important;-webkit-font-smoothing:antialiased;}}
.stApp{{background:var(--bg)!important;}}
.main .block-container{{padding:0!important;max-width:100%!important;}}
#MainMenu,footer,header,.stDeployButton{{visibility:hidden;display:none;}}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"]{{background:var(--bg2)!important;border-right:1px solid var(--border2)!important;}}
section[data-testid="stSidebar"]>div{{background:var(--bg2)!important;padding:0!important;}}
section[data-testid="stSidebar"] *{{color:var(--text)!important;}}
section[data-testid="stSidebar"] hr{{border:none!important;border-top:1px solid var(--border)!important;margin:0!important;}}
section[data-testid="stSidebar"] .element-container{{padding:0 14px!important;}}
section[data-testid="stSidebar"] .stButton>button{{
  background:var(--gold-bg2)!important;color:var(--gold2)!important;
  border:1px solid rgba(232,184,75,0.30)!important;border-radius:var(--r-sm)!important;
  font-weight:600!important;font-size:0.84rem!important;padding:9px 14px!important;
  width:100%!important;letter-spacing:0.01em!important;transition:all 0.14s!important;
}}
section[data-testid="stSidebar"] .stButton>button:hover{{
  background:rgba(232,184,75,0.24)!important;border-color:var(--gold)!important;
  box-shadow:0 0 0 3px rgba(232,184,75,0.10)!important;
}}

/* brand */
.sb-brand{{padding:20px 18px 16px;border-bottom:1px solid var(--border);}}
.sb-logo{{font-family:'Lora',serif;font-size:1.55rem;font-weight:600;letter-spacing:-0.01em;line-height:1;margin-bottom:4px;}}
.sb-logo b{{color:var(--gold);font-weight:600;}}
.sb-logo span{{color:var(--text);}}
.sb-tagline{{font-size:0.67rem;color:var(--text3);text-transform:uppercase;letter-spacing:0.15em;font-weight:500;}}
.sb-newchat{{padding:14px 14px 0;}}
.sb-section{{font-size:0.63rem;font-weight:700;text-transform:uppercase;letter-spacing:0.16em;color:var(--text3);padding:14px 18px 8px;}}

/* chat list */
.ch-item{{margin:0 8px 2px;padding:9px 11px;border-radius:var(--r-sm);border:1px solid transparent;transition:all 0.13s;}}
.ch-item:hover{{background:var(--bg3);border-color:var(--border);}}
.ch-item.active{{background:var(--gold-bg2);border-color:rgba(232,184,75,0.28);}}
.ch-title{{font-size:0.81rem;font-weight:500;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:170px;margin-bottom:3px;}}
.ch-item.active .ch-title{{color:var(--gold2);}}
.ch-meta{{display:flex;align-items:center;gap:5px;font-size:0.67rem;color:var(--text3);}}
.ch-badge{{font-family:'JetBrains Mono',monospace;font-size:0.59rem;background:rgba(232,184,75,0.10);color:var(--gold)!important;padding:1px 5px;border-radius:4px;border:1px solid rgba(232,184,75,0.15);}}

.ch-open-btn button{{background:transparent!important;color:var(--text2)!important;border:1px solid var(--border2)!important;border-radius:6px!important;font-size:0.73rem!important;padding:3px 10px!important;transition:all 0.12s!important;}}
.ch-open-btn button:hover{{background:var(--bg4)!important;color:var(--text)!important;border-color:var(--border3)!important;}}
.ch-del-btn button{{background:transparent!important;color:var(--text3)!important;border:none!important;padding:4px 6px!important;font-size:0.82rem!important;border-radius:6px!important;transition:all 0.12s!important;}}
.ch-del-btn button:hover{{background:rgba(232,92,114,0.13)!important;color:var(--crimson)!important;}}

.sb-footer{{padding:14px 18px;border-top:1px solid var(--border);font-size:0.70rem;color:var(--text3);line-height:1.55;}}
.sb-stat{{display:flex;align-items:center;gap:6px;margin-bottom:8px;font-size:0.71rem;color:var(--text2);}}
.sb-dot{{width:6px;height:6px;border-radius:50%;background:var(--green);flex-shrink:0;}}

/* ── TOP BAR ── */
.top-bar{{display:flex;align-items:center;justify-content:space-between;padding:16px 28px 14px;border-bottom:1px solid var(--border2);background:var(--bg);position:sticky;top:0;z-index:100;backdrop-filter:blur(8px);}}
.tb-logo{{display:flex;align-items:center;gap:10px;}}
.tb-icon{{width:32px;height:32px;background:var(--gold);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:1.05rem;color:var(--bg)!important;flex-shrink:0;font-weight:700;}}
.tb-name{{font-family:'Lora',serif;font-size:1.45rem;font-weight:600;color:var(--text);letter-spacing:-0.01em;line-height:1;}}
.tb-name em{{font-style:normal;color:var(--gold);}}
.tb-chat-pill{{display:flex;align-items:center;gap:10px;background:var(--bg3);border:1px solid var(--border2);border-radius:20px;padding:5px 14px 5px 10px;}}
.tb-chat-dot{{width:7px;height:7px;border-radius:50%;background:var(--green);flex-shrink:0;}}
.tb-chat-title{{font-size:0.82rem;font-weight:500;color:var(--text);max-width:260px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.tb-chat-id{{font-family:'JetBrains Mono',monospace;font-size:0.63rem;color:var(--text3);border-left:1px solid var(--border2);padding-left:10px;}}

/* ── MESSAGES ── */
.msgs-wrap{{padding:24px 28px 16px;}}
.msg-row{{display:flex;gap:12px;margin-bottom:20px;animation:msgIn 0.18s ease;}}
@keyframes msgIn{{from{{opacity:0;transform:translateY(6px);}}to{{opacity:1;transform:translateY(0);}}}}

.av{{width:34px;height:34px;border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px;font-weight:700;letter-spacing:0.02em;}}
.av-you{{background:var(--bg4);color:var(--gold)!important;border:1px solid var(--border3);font-size:0.62rem;font-family:'JetBrains Mono',monospace;}}
.av-lex{{background:var(--gold);color:var(--bg)!important;font-family:'Lora',serif;font-size:0.95rem;border:1px solid var(--gold2);}}

.msg-body{{flex:1;min-width:0;}}
.user-row{{flex-direction:row-reverse;}}
.user-row .msg-body{{display:flex;justify-content:flex-end;}}

.bubble-user{{display:inline-block;max-width:78%;background:var(--bg4);border:1px solid var(--border3);border-radius:16px 4px 16px 16px;padding:12px 16px;font-size:0.92rem;line-height:1.68;color:var(--text)!important;word-break:break-word;}}

.bubble-lex{{max-width:100%;background:var(--bg3);border:1px solid var(--border2);border-radius:4px 16px 16px 16px;padding:15px 18px;font-size:0.92rem;line-height:1.78;color:var(--text)!important;word-break:break-word;}}
.bubble-lex strong{{color:var(--crimson)!important;font-weight:600;}}
.bubble-lex em{{color:var(--text2);font-style:italic;}}
.bubble-lex blockquote{{margin:10px 0;padding:8px 12px;border-left:3px solid var(--gold);background:var(--gold-bg);border-radius:0 var(--r-sm) var(--r-sm) 0;color:var(--text2)!important;font-style:italic;}}
.bubble-lex code{{background:var(--bg4);color:var(--gold2);padding:2px 6px;border-radius:4px;font-family:'JetBrains Mono',monospace;font-size:0.86em;border:1px solid var(--border3);}}
.bubble-lex ul,.bubble-lex ol{{padding-left:1.4em;margin:6px 0;}}
.bubble-lex li{{margin-bottom:5px;}}

.cursor{{display:inline-block;width:2px;height:1em;background:var(--gold);border-radius:1px;margin-left:2px;vertical-align:text-bottom;animation:blink 0.65s step-end infinite;}}
@keyframes blink{{50%{{opacity:0;}}}}

.cite-row{{display:flex;flex-wrap:wrap;gap:5px;margin:6px 0 14px 46px;}}
.cite-chip{{display:inline-flex;align-items:center;gap:4px;background:var(--bg3);border:1px solid var(--border3);border-radius:20px;padding:3px 10px 3px 8px;font-size:0.70rem;font-family:'JetBrains Mono',monospace;color:var(--text2)!important;white-space:nowrap;}}
.cite-dot{{width:5px;height:5px;border-radius:50%;background:var(--gold);flex-shrink:0;}}

/* ── REF CARDS ── */
.ref-card{{background:var(--bg3);border:1px solid var(--border2);border-left:3px solid var(--gold);border-radius:0 var(--r) var(--r) 0;padding:13px 16px;margin-bottom:10px;transition:border-color 0.14s;}}
.ref-card:hover{{border-left-color:var(--gold2);border-color:var(--border3);}}
.ref-top{{display:flex;align-items:flex-start;justify-content:space-between;gap:8px;margin-bottom:5px;}}
.ref-act{{font-family:'Lora',serif;font-size:0.88rem;font-weight:600;color:var(--crimson)!important;line-height:1.3;flex:1;}}
.ref-sec{{font-family:'JetBrains Mono',monospace;font-size:0.70rem;background:var(--gold);color:var(--bg)!important;padding:3px 9px;border-radius:5px;white-space:nowrap;flex-shrink:0;font-weight:500;}}
.ref-title{{font-size:0.88rem;font-weight:600;color:var(--text)!important;margin-bottom:5px;line-height:1.4;}}
.ref-domain{{display:inline-block;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.10em;color:var(--green)!important;border:1px solid rgba(62,207,142,0.28);background:rgba(62,207,142,0.08);padding:2px 9px;border-radius:20px;margin-bottom:9px;font-weight:600;}}
.ref-bar-wrap{{height:2px;background:var(--bg4);border-radius:2px;margin-bottom:10px;overflow:hidden;}}
.ref-bar-fill{{height:100%;background:linear-gradient(90deg,var(--gold),var(--crimson));border-radius:2px;}}
.ref-text{{font-size:0.80rem;color:var(--text2)!important;line-height:1.68;font-family:'JetBrains Mono',monospace;border-top:1px solid var(--border);padding-top:9px;margin-top:4px;white-space:pre-wrap;word-break:break-word;}}
.ref-text.clamped{{display:-webkit-box;-webkit-line-clamp:5;-webkit-box-orient:vertical;overflow:hidden;}}
.vm-btn>button{{background:transparent!important;color:var(--gold)!important;border:1px solid rgba(232,184,75,0.22)!important;border-radius:6px!important;font-size:0.73rem!important;padding:3px 10px!important;margin-top:5px!important;transition:all 0.12s!important;}}
.vm-btn>button:hover{{background:var(--gold-bg)!important;border-color:var(--gold)!important;}}

/* ── INPUT BAR — FIXED BOTTOM ── */
/* The bar is always pinned to the bottom of the viewport.
   It never moves up during streaming. */
.input-fixed{{
  position:fixed;
  bottom:0;
  left:0;
  right:0;
  /* Offset for the Streamlit sidebar (~280px) */
  margin-left:280px;
  background:var(--bg);
  border-top:1px solid var(--border2);
  z-index:9999;
  padding:12px 28px 14px;
}}
.input-inner{{max-width:820px;margin:0 auto;}}

/* Align the form columns so input + button share the same 48px height row */
.input-fixed [data-testid="stHorizontalBlock"]{{
  align-items:center!important;
  gap:10px!important;
}}
.input-fixed [data-testid="column"]{{
  padding:0!important;
}}

.stForm,[data-testid="stForm"]{{background:transparent!important;border:none!important;padding:0!important;}}
.stTextInput>label{{display:none!important;}}
.stTextInput>div{{
  background:var(--bg3)!important;
  border:1.5px solid var(--border3)!important;
  border-radius:var(--r-lg)!important;
  transition:border-color 0.18s,box-shadow 0.18s!important;
  height:48px!important;
  display:flex!important;
  align-items:center!important;
}}
.stTextInput>div:focus-within{{border-color:var(--gold)!important;box-shadow:0 0 0 3px rgba(232,184,75,0.12)!important;}}
.stTextInput>div>div{{background:transparent!important;border:none!important;height:100%!important;}}
.stTextInput input{{
  background:transparent!important;
  border:none!important;
  color:var(--text)!important;
  font-family:'Sora',sans-serif!important;
  font-size:0.93rem!important;
  padding:0 16px!important;
  caret-color:var(--gold)!important;
  box-shadow:none!important;
  height:48px!important;
  line-height:48px!important;
}}
.stTextInput input::placeholder{{color:var(--text3)!important;}}
.stTextInput input:focus{{outline:none!important;box-shadow:none!important;border:none!important;}}

/* Send button — same 48px height as input */
[data-testid="stFormSubmitButton"]>button{{
  background:var(--gold)!important;
  color:#0c0f1a!important;
  border:none!important;
  border-radius:var(--r-lg)!important;
  font-weight:700!important;
  font-size:0.88rem!important;
  letter-spacing:0.02em!important;
  transition:all 0.14s!important;
  white-space:nowrap!important;
  height:48px!important;
  width:100%!important;
  padding:0 20px!important;
  display:flex!important;
  align-items:center!important;
  justify-content:center!important;
}}
[data-testid="stFormSubmitButton"]>button:hover{{background:var(--gold2)!important;box-shadow:0 4px 18px rgba(232,184,75,0.28)!important;}}
[data-testid="stFormSubmitButton"]>button:active{{transform:scale(0.97)!important;}}
.input-hint{{font-size:0.67rem;color:var(--text3);margin-top:7px;text-align:center;}}

/* Responsive — on mobile sidebar collapses so no left offset */
@media(max-width:992px){{
  .input-fixed{{margin-left:0;padding:10px 16px 12px;}}
}}

/* ── JS-POWERED VIEW MORE BUTTON (no scroll-to-top) ── */
.vm-js-btn{{
  display:inline-flex;
  align-items:center;
  gap:4px;
  background:transparent;
  color:var(--gold);
  border:1px solid rgba(232,184,75,0.25);
  border-radius:6px;
  font-size:0.73rem;
  font-family:'Sora',sans-serif;
  padding:4px 11px;
  margin-top:7px;
  cursor:pointer;
  transition:all 0.12s;
}}
.vm-js-btn:hover{{background:var(--gold-bg);border-color:var(--gold);}}

/* Source link */
.ref-src-link{{
  display:inline-block;
  margin-top:8px;
  font-size:0.72rem;
  color:var(--gold);
  text-decoration:none;
  opacity:0.8;
}}
.ref-src-link:hover{{opacity:1;}}

/* ── MISC ── */
.streamlit-expanderHeader{{background:var(--bg3)!important;border:1px solid var(--border2)!important;border-radius:var(--r-sm)!important;color:var(--text2)!important;font-size:0.82rem!important;font-weight:500!important;}}
.streamlit-expanderContent{{background:var(--bg)!important;border:1px solid var(--border2)!important;border-top:none!important;border-radius:0 0 var(--r-sm) var(--r-sm)!important;padding:14px!important;}}
[data-testid="stStatusWidget"],.stStatus{{background:var(--bg3)!important;border:1px solid var(--border2)!important;border-radius:var(--r-sm)!important;color:var(--text2)!important;}}
hr{{border:none!important;border-top:1px solid var(--border)!important;margin:12px 0!important;}}
.stAlert{{border-radius:var(--r-sm)!important;}}
::-webkit-scrollbar{{width:4px;}}::-webkit-scrollbar-track{{background:transparent;}}::-webkit-scrollbar-thumb{{background:var(--border3);border-radius:4px;}}::-webkit-scrollbar-thumb:hover{{background:var(--text3);}}

/* ── WELCOME ── */
.welcome-wrap{{display:flex;flex-direction:column;align-items:center;padding:64px 28px 44px;text-align:center;}}
.welcome-seal{{width:72px;height:72px;background:var(--bg3);border:1px solid var(--border3);border-radius:20px;display:flex;align-items:center;justify-content:center;font-size:2rem;margin-bottom:22px;}}
.welcome-h{{font-family:'Lora',serif;font-size:2rem;font-weight:600;color:var(--text);margin-bottom:12px;letter-spacing:-0.01em;}}
.welcome-h span{{color:var(--gold);}}
.welcome-p{{font-size:0.91rem;color:var(--text2);max-width:460px;line-height:1.78;margin-bottom:32px;}}
.feat-pills{{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;max-width:520px;}}
.feat-pill{{display:inline-flex;align-items:center;gap:6px;background:var(--bg3);border:1px solid var(--border2);border-radius:20px;padding:6px 14px;font-size:0.77rem;color:var(--text2);}}
.fp-dot{{width:5px;height:5px;background:var(--gold);border-radius:50%;}}

@media(max-width:768px){{
  .top-bar{{padding:12px 16px;}}.tb-chat-pill{{display:none;}}
  .msgs-wrap{{padding:16px;}}
  .bubble-user{{max-width:94%;}}.welcome-h{{font-size:1.6rem;}}
}}
"""


def inject_css() -> None:
    """Inject all CSS. Call once at top of main()."""
    st.markdown(f"<style>{_CSS.format(**PALETTE)}</style>", unsafe_allow_html=True)