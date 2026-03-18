"""
frontend/components/styles.py
─────────────────────────────
Call inject_css() once at app startup.
"""

import streamlit as st

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Google+Sans+Text:wght@400;500&family=Google+Sans+Display:wght@400;500;700&family=Roboto+Mono:wght@400;500&display=swap');

/* ── GEMINI DESIGN TOKENS ── */
:root {
  --bg:            #131314;
  --sidebar-bg:    #1e1f20;
  --surface:       #282a2c;
  --surface-2:     #303134;
  --surface-hover: #35363a;
  --on-surface:    #e3e3e3;
  --on-surface-2:  #9aa0a6;
  --on-surface-3:  #5f6368;
  --blue:          #8ab4f8;
  --blue-2:        #aecbfa;
  --blue-dark:     #4285f4;
  --green:         #81c995;
  --red:           #f28b82;
  --yellow:        #fdd663;
  --purple:        #c58af9;
  --border:        rgba(255,255,255,0.08);
  --border-2:      rgba(255,255,255,0.12);
  --r-xs: 4px; --r-sm: 8px; --r: 12px; --r-lg: 28px;
  --gem-grad: linear-gradient(90deg, #4285f4 0%, #9c5fed 33%, #d96570 66%, #ea4335 100%);
}

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
  font-family: 'Google Sans Text', 'Google Sans', Roboto, sans-serif !important;
  background: var(--bg) !important;
  color: var(--on-surface) !important;
  -webkit-font-smoothing: antialiased;
}
.stApp { background: var(--bg) !important; }
.main .block-container { padding: 0 !important; max-width: 100% !important; }
/* Hide Streamlit chrome — use visibility:hidden (not display:none) on header so
   child elements (sidebar toggle) can override with visibility:visible */
#MainMenu, footer, .stDeployButton { visibility: hidden; display: none; }
header { visibility: hidden; }

/* ── SIDEBAR TOGGLE ── */
/* The collapsed-control button lives inside header; keep it always visible */
section[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
  visibility: visible !important;
  display: flex !important;
}
[data-testid="collapsedControl"] {
  background: transparent !important;
  border: none !important;
  z-index: 300 !important;
  cursor: pointer !important;
  opacity: 0.75;
  transition: opacity 0.15s, background 0.15s !important;
}
[data-testid="collapsedControl"]:hover {
  opacity: 1;
  background: var(--surface) !important;
  border-radius: var(--r-sm) !important;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
  background: var(--sidebar-bg) !important;
  border-right: none !important;
  width: 350px !important;
}
section[data-testid="stSidebar"] > div {
  background: var(--sidebar-bg) !important;
  padding: 0 !important;
}
section[data-testid="stSidebar"] * { color: var(--on-surface) !important; }
section[data-testid="stSidebar"] hr {
  border: none !important;
  border-top: 1px solid var(--border) !important;
  margin: 0 !important;
}
section[data-testid="stSidebar"] .element-container { padding: 0 12px !important; }

/* Sidebar header */
.sb-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 16px 8px;
}
.sb-app-name {
  font-family: 'Google Sans', sans-serif;
  font-size: 1.25rem;
  font-weight: 700;
  background: var(--gem-grad);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.01em;
}

/* New Chat Button */
.sb-newchat { padding: 8px 12px 4px; }
.sb-newchat .stButton > button {
  background: var(--surface) !important;
  color: var(--on-surface) !important;
  border: 1px solid var(--border-2) !important;
  border-radius: var(--r-lg) !important;
  font-family: 'Google Sans Text', sans-serif !important;
  font-size: 0.875rem !important;
  font-weight: 500 !important;
  padding: 10px 20px !important;
  width: 100% !important;
  text-align: left !important;
  transition: background 0.15s ease !important;
}
.sb-newchat .stButton > button:hover {
  background: var(--surface-2) !important;
  border-color: var(--border-2) !important;
}

/* Sidebar section label */
.sb-section-label {
  padding: 12px 16px 6px;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--on-surface-2);
  -webkit-text-fill-color: var(--on-surface-2) !important;
  letter-spacing: 0.02em;
}

/* Chat list items */
.ch-row {
  margin: 1px 8px;
  border-radius: var(--r-sm);
  overflow: hidden;
}
.ch-row .stButton > button {
  background: transparent !important;
  border: none !important;
  border-radius: var(--r-sm) !important;
  color: var(--on-surface) !important;
  font-family: 'Google Sans Text', sans-serif !important;
  font-size: 0.875rem !important;
  font-weight: 400 !important;
  padding: 8px 12px !important;
  width: 100% !important;
  text-align: left !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  transition: background 0.12s ease !important;
  min-height: 40px !important;
}
.ch-row .stButton > button:hover {
  background: var(--surface-hover) !important;
}
.ch-row.active .stButton > button {
  background: var(--surface-2) !important;
  font-weight: 500 !important;
}
/* Sidebar Delete Button (Targeted structurally since wrappers don't wrap in Streamlit) */
section[data-testid="stSidebar"] [data-testid="column"]:nth-child(2) button {
  background: transparent !important;
  color: var(--on-surface-3) !important;
  border: solid !important;
  border-radius: var(--r-sm) !important;
  padding: 0 6px !important;
  font-size: 0.85rem !important;
  min-height: 36px !important;
  transition: all 0.12s !important;
  /* Shift left towards the title to leave space on the right edge */
  position: relative !important;
  right: 2px !important;
}
section[data-testid="stSidebar"] [data-testid="column"]:nth-child(2) button:hover {
  background: rgba(255, 255, 255, 0.05) !important;
  color: var(--on-surface) !important;
}

/* Sidebar footer */
.sb-footer {
  padding: 12px 16px 16px;
  border-top: 1px solid var(--border);
  font-size: 0.70rem;
  color: var(--on-surface-3);
  line-height: 1.6;
  -webkit-text-fill-color: var(--on-surface-3) !important;
}
.sb-stat {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-bottom: 8px;
  font-size: 0.75rem;
  color: var(--on-surface-2);
  -webkit-text-fill-color: var(--on-surface-2) !important;
}
.sb-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--green);
  flex-shrink: 0;
  box-shadow: 0 0 6px rgba(129,201,149,0.6);
  animation: pulse-dot 2.4s ease-in-out infinite;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* ── TOP BAR ── */
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  /* 56px left clears the Streamlit sidebar-toggle button (≈40px wide) */
  padding: 12px 28px 12px 56px;
  background: var(--bg);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid var(--border);
}
.tb-logo {
  display: flex;
  align-items: center;
  gap: 10px;
}
.tb-icon {
  width: 30px; height: 30px;
  border-radius: 50%;
  background: var(--gem-grad);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
  color: #fff !important;
  flex-shrink: 0;
}
.tb-name {
  font-family: 'Google Sans', sans-serif;
  font-size: 1.3rem;
  font-weight: 700;
  background: var(--gem-grad);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.01em;
}
.tb-model-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: 'Google Sans Text', sans-serif;
  font-size: 0.8125rem;
  color: var(--on-surface-2);
  background: var(--surface);
  border: 1px solid var(--border-2);
  border-radius: 20px;
  padding: 5px 14px;
}
.tb-model-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--gem-grad);
  flex-shrink: 0;
}
.tb-chat-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'Google Sans Text', sans-serif;
  font-size: 0.875rem;
  color: var(--on-surface-2);
  background: var(--surface);
  border: 1px solid var(--border-2);
  border-radius: 20px;
  padding: 5px 14px 5px 10px;
}
.tb-chat-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--green);
  box-shadow: 0 0 6px rgba(129,201,149,0.6);
  flex-shrink: 0;
  animation: pulse-dot 2.4s ease-in-out infinite;
}
.tb-chat-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--on-surface);
  max-width: 280px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.tb-chat-id {
  font-family: 'Roboto Mono', monospace;
  font-size: 0.6875rem;
  color: var(--on-surface-3);
  border-left: 1px solid var(--border-2);
  padding-left: 10px;
}

/* ── MESSAGES ── */
.msgs-wrap {
  padding: 32px 0 28px;
  max-width: 1000px;
  width: 80%;
  margin: 0 auto;
  position: relative;
}
.msg-row {
  display: flex;
  gap: 16px;
  margin: 0 auto 28px;
  max-width: 1000px;
  width: 80%;
  animation: msgIn 0.2s ease;
  /* Generous side padding so text never touches viewport edges */
  padding: 0 32px;
}
@keyframes msgIn {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Avatars */
.av {
  width: 32px; height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 3px;
  font-weight: 600;
  font-size: 0.75rem;
  letter-spacing: 0.01em;
}
.av-you {
  background: var(--surface-2);
  color: var(--on-surface) !important;
  font-family: 'Google Sans', sans-serif;
  border: 1px solid var(--border-2);
}
.av-lex {
  background: var(--gem-grad);
  color: #fff !important;
  font-size: 1rem;
  border: none;
}

/* User bubbles */
.msg-body { flex: 1; min-width: 0; }
.user-row { flex-direction: row-reverse; }
.user-row .msg-body { display: flex; justify-content: flex-end; }

.bubble-user {
  display: inline-block;
  max-width: 80%;
  background: var(--surface);
  border: 1px solid var(--border-2);
  border-radius: 20px 20px 4px 20px;
  padding: 12px 18px;
  font-size: 0.9375rem;
  line-height: 1.65;
  color: var(--on-surface) !important;
  word-break: break-word;
}

/* AI message — no bubble, just text */
.bubble-lex {
  max-width: 100%;
  font-size: 0.9375rem;
  line-height: 1.75;
  color: var(--on-surface) !important;
  word-break: break-word;
}
.bubble-lex strong { color: var(--blue-2) !important; font-weight: 600; }
.bubble-lex em { color: var(--on-surface-2); font-style: italic; }
.bubble-lex blockquote {
  margin: 10px 0;
  padding: 10px 14px;
  border-left: 3px solid var(--blue-dark);
  background: rgba(66,133,244,0.08);
  border-radius: 0 var(--r-sm) var(--r-sm) 0;
  color: var(--on-surface-2) !important;
}
.bubble-lex code {
  background: var(--surface);
  color: var(--blue-2);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Roboto Mono', monospace;
  font-size: 0.875em;
  border: 1px solid var(--border-2);
}
.bubble-lex ul, .bubble-lex ol { padding-left: 1.4em; margin: 6px 0; }
.bubble-lex li { margin-bottom: 5px; }
.bubble-lex h1, .bubble-lex h2, .bubble-lex h3 {
  color: var(--on-surface) !important;
  margin: 12px 0 6px;
}

/* Streaming cursor */
.cursor {
  display: inline-block;
  width: 2px; height: 1em;
  background: var(--blue);
  border-radius: 1px;
  margin-left: 2px;
  vertical-align: text-bottom;
  animation: blink 0.65s step-end infinite;
}
@keyframes blink { 50% { opacity: 0; } }

/* Citation chips */
.cite-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 8px auto 16px;
  padding: 0 32px 0 80px;
  max-width: 1000px;
  width: 80%;
}
.cite-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: var(--surface);
  border: 1px solid var(--border-2);
  border-radius: 20px;
  padding: 4px 12px;
  font-size: 0.75rem;
  font-family: 'Roboto Mono', monospace;
  color: var(--on-surface-2) !important;
  white-space: nowrap;
  transition: border-color 0.12s;
}
.cite-chip:hover { border-color: var(--blue-dark); }
.cite-dot {
  width: 5px; height: 5px;
  border-radius: 50%;
  background: var(--blue);
  flex-shrink: 0;
}

/* ── REF CARDS ── */
.ref-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 16px;
  margin-bottom: 10px;
  transition: border-color 0.18s, background 0.18s;
  position: relative;
}
.ref-card:hover {
  background: var(--surface-2);
  border-color: var(--border-2);
}
.ref-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 6px;
}
.ref-right {
  display: flex;
  align-items: center;
  gap: 7px;
  flex-shrink: 0;
}
.ref-act {
  font-family: 'Google Sans', sans-serif;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--blue-2) !important;
  line-height: 1.3;
  flex: 1;
}
.ref-sec {
  font-family: 'Roboto Mono', monospace;
  font-size: 0.75rem;
  background: rgba(66,133,244,0.15);
  color: var(--blue-2) !important;
  padding: 3px 10px;
  border-radius: 20px;
  white-space: nowrap;
  flex-shrink: 0;
  font-weight: 500;
  border: 1px solid rgba(66,133,244,0.25);
}
.ref-copy-btn {
  background: var(--surface-2);
  color: var(--on-surface-2);
  border: 1px solid var(--border-2);
  border-radius: 20px;
  font-size: 0.75rem;
  font-family: 'Google Sans Text', sans-serif;
  font-weight: 500;
  padding: 3px 10px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.ref-copy-btn:hover {
  background: rgba(66,133,244,0.15);
  border-color: rgba(66,133,244,0.4);
  color: var(--blue-2);
}
.ref-title {
  font-size: 0.9375rem;
  font-weight: 500;
  color: var(--on-surface) !important;
  margin-bottom: 6px;
  line-height: 1.4;
}
.ref-domain {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.6875rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--green) !important;
  border: 1px solid rgba(129,201,149,0.25);
  background: rgba(129,201,149,0.08);
  padding: 2px 10px;
  border-radius: 20px;
  margin-bottom: 10px;
  font-weight: 600;
}
.ref-bar-wrap {
  height: 2px;
  background: var(--surface-2);
  border-radius: 2px;
  margin-bottom: 12px;
  overflow: hidden;
}
.ref-bar-fill {
  height: 100%;
  background: var(--gem-grad);
  border-radius: 2px;
  position: relative;
  overflow: hidden;
}
.ref-bar-fill::after {
  content: '';
  position: absolute;
  top: 0; left: -100%; right: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
  animation: shimmer 2.5s ease-in-out infinite;
}
@keyframes shimmer { to { left: 200%; right: -100%; } }
.ref-text {
  font-size: 0.8125rem;
  color: var(--on-surface-2) !important;
  line-height: 1.7;
  font-family: 'Roboto Mono', monospace;
  border-top: 1px solid var(--border);
  padding-top: 10px;
  margin-top: 5px;
  white-space: pre-wrap;
  word-break: break-word;
}
.ref-text.clamped {
  display: -webkit-box;
  -webkit-line-clamp: 5;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.vm-js-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: transparent;
  color: var(--blue);
  border: 1px solid rgba(138,180,248,0.3);
  border-radius: 20px;
  font-size: 0.75rem;
  font-family: 'Google Sans Text', sans-serif;
  padding: 4px 12px;
  margin-top: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.vm-js-btn:hover {
  background: rgba(66,133,244,0.1);
  border-color: var(--blue);
}
.ref-src-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: 10px;
  font-size: 0.75rem;
  color: var(--blue);
  text-decoration: none;
  opacity: 0.8;
  transition: opacity 0.15s;
}
.ref-src-link:hover { opacity: 1; }

/* ── EXPANDER (ref section) ── */
[data-testid="stExpander"] {
  max-width: 1000px;
  width: 80%;
  margin: 0 auto;
}
.streamlit-expanderHeader {
  background: var(--surface) !important;
  border: 1px solid var(--border-2) !important;
  border-radius: var(--r-sm) !important;
  color: var(--on-surface-2) !important;
  font-family: 'Google Sans Text', sans-serif !important;
  font-size: 0.875rem !important;
  font-weight: 500 !important;
  padding: 10px 14px !important;
  transition: background 0.15s !important;
}
.streamlit-expanderHeader:hover {
  background: var(--surface-2) !important;
}
.streamlit-expanderContent {
  background: var(--bg) !important;
  border: 1px solid var(--border-2) !important;
  border-top: none !important;
  border-radius: 0 0 var(--r-sm) var(--r-sm) !important;
  padding: 14px !important;
}

/* ── INPUT BAR ── */
.input-fixed {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  margin-left: 280px;
  background: var(--bg);
  z-index: 9999;
  /* Comfortable side padding so pill doesn't stretch to viewport edges */
  padding: 12px 48px 20px;
}
.input-inner {
  /* Max width matches the chat content column — centred with auto margins */
  max-width: 680px;
  width: 80%;
  margin: 0 auto;
}
.input-fixed [data-testid="stHorizontalBlock"] {
  align-items: center !important;
  gap: 10px !important;
}
.input-fixed [data-testid="column"] { padding: 0 !important; }

.stForm, [data-testid="stForm"] {
  background: var(--surface) !important;
  border: 1px solid var(--border-2) !important;
  border-radius: 28px !important;
  padding: 4px 6px 4px 20px !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
  /* Force the pill itself to be constrained and centered */
  max-width: 1000px !important;
  width: calc(100% - 32px) !important;
  margin: 0 auto !important;
}
.stForm:focus-within, [data-testid="stForm"]:focus-within {
  border-color: var(--blue-dark) !important;
  box-shadow: 0 0 0 2px rgba(66,133,244,0.15) !important;
}
.stTextInput > label { display: none !important; }
.stTextInput > div {
  background: transparent !important;
  border: none !important;
  border-radius: 0 !important;
  height: 52px !important;
  display: flex !important;
  align-items: center !important;
  box-shadow: none !important;
}
.stTextInput > div:focus-within {
  border: none !important;
  box-shadow: none !important;
}
.stTextInput > div > div {
  background: transparent !important;
  border: none !important;
  height: 100% !important;
}
.stTextInput input {
  background: transparent !important;
  border: none !important;
  color: var(--on-surface) !important;
  font-family: 'Google Sans Text', sans-serif !important;
  font-size: 0.9375rem !important;
  padding: 0 !important;
  caret-color: var(--blue) !important;
  box-shadow: none !important;
  height: 52px !important;
  line-height: 52px !important;
}
.stTextInput input::placeholder { color: var(--on-surface-3) !important; }
.stTextInput input:focus {
  outline: none !important;
  box-shadow: none !important;
  border: none !important;
}

/* Send button — Gemini style gradient circle */
[data-testid="stFormSubmitButton"] > button {
  background: var(--gem-grad) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 50% !important;
  width: 44px !important;
  height: 44px !important;
  min-height: 44px !important;
  padding: 0 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  font-size: 1.1rem !important;
  font-weight: 700 !important;
  transition: opacity 0.15s, transform 0.15s !important;
  flex-shrink: 0 !important;
  margin-left: 27px !important;
  margin-top: 3px !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
  opacity: 0.88 !important;
  transform: scale(1.05) !important;
}
[data-testid="stFormSubmitButton"] > button:active {
  transform: scale(0.95) !important;
}

.input-hint {
  font-size: 0.6875rem;
  color: var(--on-surface-3);
  margin-top: 8px;
  text-align: center;
  font-family: 'Google Sans Text', sans-serif;
}
.input-hint kbd {
  font-family: 'Roboto Mono', monospace;
  font-size: 0.625rem;
  background: var(--surface);
  border: 1px solid var(--border-2);
  border-radius: 3px;
  padding: 1px 5px;
  color: var(--on-surface-3);
}

@media (max-width: 992px) {
  .input-fixed { margin-left: 0; padding: 10px 16px 16px; }
  .input-inner { max-width: 100%; }
  .tb-chat-pill { display: none; }
}

/* ── WELCOME — Gemini Style ── */
.welcome-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80px 32px 120px;
  text-align: center;
  max-width: 768px;
  margin: 0 auto;
  animation: fadeUp 0.4s cubic-bezier(0.2, 0, 0, 1);
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}
.welcome-greeting {
  font-family: 'Google Sans Display', 'Google Sans', sans-serif;
  font-size: 3rem;
  font-weight: 700;
  line-height: 1.15;
  letter-spacing: -0.02em;
  margin-bottom: 10px;
}
.welcome-greeting .grad-text {
  background: var(--gem-grad);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.welcome-subtitle {
  font-size: 1.125rem;
  color: var(--on-surface-2);
  margin-bottom: 40px;
  line-height: 1.6;
}
.suggestion-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  width: 100%;
  max-width: 620px;
}
.suggestion-card {
  background: var(--surface);
  border: 1px solid var(--border-2);
  border-radius: var(--r);
  padding: 14px 16px;
  text-align: left;
  cursor: default;
  transition: background 0.18s, border-color 0.18s;
  position: relative;
  overflow: hidden;
}
.suggestion-card:hover {
  background: var(--surface-2);
  border-color: rgba(138,180,248,0.35);
}
.suggestion-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: var(--gem-grad);
  opacity: 0;
  transition: opacity 0.2s;
}
.suggestion-card:hover::before { opacity: 1; }
.suggestion-icon { font-size: 1.25rem; margin-bottom: 8px; }
.suggestion-title {
  font-family: 'Google Sans', sans-serif;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--on-surface);
  margin-bottom: 3px;
  line-height: 1.3;
}
.suggestion-desc {
  font-size: 0.8125rem;
  color: var(--on-surface-2);
  line-height: 1.5;
}

/* ── MISC ── */
[data-testid="stStatusWidget"], .stStatus {
  background: var(--surface) !important;
  border: 1px solid var(--border-2) !important;
  border-radius: var(--r-sm) !important;
  color: var(--on-surface-2) !important;
}
hr {
  border: none !important;
  border-top: 1px solid var(--border) !important;
  margin: 12px 0 !important;
}
.stAlert { border-radius: var(--r-sm) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: var(--surface-2);
  border-radius: 6px;
}
::-webkit-scrollbar-thumb:hover { background: var(--surface-hover); }

@media (max-width: 768px) {
  .welcome-wrap { padding: 50px 16px 110px; }
  .welcome-greeting { font-size: 2.2rem; }
  .suggestion-grid { grid-template-columns: 1fr; }
  .msgs-wrap { padding: 16px 0 16px; }
  .bubble-user { max-width: 92%; }
}
"""


_SIDEBAR_RESIZE_JS = """
<script>
(function() {
  function initResize() {
    var sidebar = window.parent.document.querySelector('section[data-testid="stSidebar"]');
    if (!sidebar) { setTimeout(initResize, 600); return; }

    var handle = window.parent.document.getElementById('__lex_sb_handle');
    if (!handle) {
      handle = window.parent.document.createElement('div');
      handle.id = '__lex_sb_handle';
      Object.assign(handle.style, {
        position: 'absolute', top: '0', right: '-4px', bottom: '0',
        width: '8px', cursor: 'col-resize', zIndex: '9999',
        transition: 'background 0.15s',
      });
      handle.addEventListener('mouseenter', function() {
        handle.style.background = 'rgba(138,180,248,0.25)';
      });
      handle.addEventListener('mouseleave', function() {
        if (!dragging) handle.style.background = '';
      });
      sidebar.style.position = 'relative';
      sidebar.appendChild(handle);
    }

    var dragging = false, startX, startW;
    var MIN_W = 160, MAX_W = 480;

    handle.addEventListener('mousedown', function(e) {
      dragging = true; startX = e.clientX;
      startW = sidebar.getBoundingClientRect().width;
      handle.style.background = 'rgba(138,180,248,0.45)';
      window.parent.document.body.style.userSelect = 'none';
      window.parent.document.body.style.cursor = 'col-resize';
    });
    window.parent.document.addEventListener('mousemove', function(e) {
      if (!dragging) return;
      var newW = Math.min(MAX_W, Math.max(MIN_W, startW + (e.clientX - startX)));
      sidebar.style.width = newW + 'px'; sidebar.style.minWidth = newW + 'px';
      var bar = window.parent.document.querySelector('.input-fixed');
      if (bar) bar.style.marginLeft = newW + 'px';
    });
    window.parent.document.addEventListener('mouseup', function() {
      if (!dragging) return;
      dragging = false; handle.style.background = '';
      window.parent.document.body.style.userSelect = '';
      window.parent.document.body.style.cursor = '';
    });
  }
  if (window.parent.document.readyState === 'loading') {
    window.parent.document.addEventListener('DOMContentLoaded', initResize);
  } else { initResize(); }
})();
</script>
"""


def inject_css() -> None:
    """Inject CSS + sidebar-resize JS. Call once at top of main()."""
    st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)
    st.markdown(_SIDEBAR_RESIZE_JS, unsafe_allow_html=True)