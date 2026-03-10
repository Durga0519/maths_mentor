import sys, os, time, re, json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from tools.ocr  import extract_text_from_image
from tools.asr  import transcribe_audio
from agents.workflow import graph
from memory.memory_store import store_solution, get_similar_problem, get_recent_history
# ──────────────────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────────────────
st.set_page_config(page_title="AI Math Mentor", page_icon="📐",
                   layout="wide", initial_sidebar_state="expanded")

# ──────────────────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;0,700;1,400&family=Source+Sans+3:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --cream:#faf8f3; --parchment:#f2ede0; --warm-tan:#e8dcc8;
    --ink:#1c1a16; --ink-muted:#4a4540; --ink-faint:#8c857a;
    --rust:#b85c2c; --rust-light:#d4784a;
    --forest:#2d5a3d; --forest-light:#4a7c5f;
    --gold:#c9943a; --gold-light:#e0b860; --blue-ink:#2c4a7c;
    --shadow-sm:0 2px 8px rgba(28,26,22,0.10);
    --shadow-md:0 4px 20px rgba(28,26,22,0.14);
    --shadow-lg:0 8px 40px rgba(28,26,22,0.18);
    --radius:10px; --radius-lg:16px;
}
html,body,[data-testid="stAppViewContainer"]{background-color:var(--cream)!important;font-family:'Source Sans 3',sans-serif;color:var(--ink);}
[data-testid="stAppViewContainer"]>.main{background-color:var(--cream)!important;}
#MainMenu,footer,header{visibility:hidden;}
[data-testid="stToolbar"]{display:none!important;}

[data-testid="stSidebar"]{background:var(--ink)!important;border-right:3px solid var(--rust)!important;}
[data-testid="stSidebar"] *{color:var(--cream)!important;}
[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3{color:var(--gold-light)!important;font-family:'Lora',serif;}

[data-testid="collapsedControl"]{display:flex!important;visibility:visible!important;background:var(--rust)!important;border-radius:0 8px 8px 0!important;width:28px!important;align-items:center!important;justify-content:center!important;box-shadow:2px 0 10px rgba(184,92,44,0.4)!important;z-index:9999!important;top:50%!important;transform:translateY(-50%)!important;}
[data-testid="collapsedControl"] svg{fill:white!important;color:white!important;}
[data-testid="collapsedControl"]:hover{background:var(--rust-light)!important;width:34px!important;}

.sidebar-toggle-btn{position:fixed;top:50%;left:0;transform:translateY(-50%);z-index:99999;background:var(--rust);color:white;border:none;border-radius:0 10px 10px 0;padding:14px 10px;cursor:pointer;box-shadow:3px 0 14px rgba(184,92,44,0.45);writing-mode:vertical-rl;letter-spacing:0.06em;font-family:'Source Sans 3',sans-serif;font-weight:700;font-size:0.72rem;transition:all 0.2s ease;}
.sidebar-toggle-btn:hover{background:var(--rust-light);padding-left:14px;}

.page-header{background:var(--ink);color:var(--cream);padding:1.6rem 2.5rem;border-radius:var(--radius-lg);margin-bottom:1.6rem;position:relative;overflow:hidden;box-shadow:var(--shadow-lg);}
.page-header::before{content:"∑  ∫  π  √  ∂  ∞  Δ  ∇  λ  φ";position:absolute;top:14px;right:24px;font-family:'JetBrains Mono',monospace;font-size:0.72rem;color:rgba(201,148,58,0.20);letter-spacing:0.25em;white-space:nowrap;}
.page-header h1{font-family:'Lora',serif;font-size:1.9rem;font-weight:700;color:var(--cream);margin:0 0 0.2rem;}
.page-header p{font-size:0.88rem;color:var(--gold-light);margin:0;font-style:italic;font-family:'Lora',serif;}

.pipeline-bar{background:var(--ink);border-radius:var(--radius-lg);padding:0.85rem 1.5rem;margin-bottom:1.5rem;display:flex;align-items:center;flex-wrap:wrap;gap:2px;box-shadow:var(--shadow-sm);}
.pipeline-bar-label{font-family:'Source Sans 3',sans-serif;font-size:0.72rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:rgba(250,248,243,0.35);margin-right:0.9rem;white-space:nowrap;}
.pipe-step{display:flex;align-items:center;gap:0.45rem;padding:0.35rem 0.85rem;border-radius:20px;font-size:0.82rem;font-family:'Source Sans 3',sans-serif;font-weight:600;white-space:nowrap;transition:all 0.3s ease;}
.pipe-step.pending{color:rgba(250,248,243,0.28);}
.pipe-step.active{background:rgba(201,148,58,0.18);color:#e0b860;animation:pulse-pipe 1.2s ease-in-out infinite;}
.pipe-step.done{background:rgba(45,90,61,0.25);color:#7ec99a;}
.pipe-arrow{color:rgba(250,248,243,0.15);font-size:0.8rem;padding:0 0.15rem;}
.pipe-dot{width:7px;height:7px;border-radius:50%;flex-shrink:0;}
.pipe-dot.pending{background:rgba(250,248,243,0.15);}
.pipe-dot.active{background:#c9943a;box-shadow:0 0 7px #c9943a;}
.pipe-dot.done{background:#7ec99a;}
@keyframes pulse-pipe{0%,100%{opacity:1}50%{opacity:0.5}}

[data-testid="stTabs"] [role="tablist"]{background:var(--parchment);border-radius:var(--radius);padding:4px;border:1px solid var(--warm-tan);}
[data-testid="stTabs"] [role="tab"]{font-family:'Source Sans 3',sans-serif;font-weight:600;font-size:0.875rem;color:var(--ink-muted)!important;border-radius:7px!important;padding:0.4rem 1.1rem!important;transition:all 0.2s ease;border:none!important;}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{background:var(--ink)!important;color:var(--cream)!important;}
[data-testid="stTabs"] [role="tab"]:hover:not([aria-selected="true"]){background:var(--warm-tan)!important;color:var(--ink)!important;}

.stTextArea textarea,.stTextInput input{background:var(--parchment)!important;border:1.5px solid var(--warm-tan)!important;border-radius:var(--radius)!important;font-family:'Source Sans 3',sans-serif!important;font-size:0.95rem!important;color:var(--ink)!important;padding:0.75rem 1rem!important;}
.stTextArea textarea:focus,.stTextInput input:focus{border-color:var(--rust)!important;box-shadow:0 0 0 3px rgba(184,92,44,0.15)!important;}
.stTextArea label,.stTextInput label,[data-testid="stFileUploader"] label{font-family:'Source Sans 3',sans-serif!important;font-weight:600!important;font-size:0.78rem!important;color:var(--ink-muted)!important;letter-spacing:0.06em!important;text-transform:uppercase!important;}
[data-testid="stFileUploader"]{background:var(--parchment)!important;border:2px dashed var(--warm-tan)!important;border-radius:var(--radius-lg)!important;}
[data-testid="stFileUploader"]:hover{border-color:var(--rust)!important;}

.stButton>button{background:var(--rust)!important;color:white!important;font-family:'Source Sans 3',sans-serif!important;font-weight:600!important;font-size:1rem!important;letter-spacing:0.04em!important;border:none!important;border-radius:var(--radius)!important;padding:0.65rem 2rem!important;box-shadow:0 3px 12px rgba(184,92,44,0.35)!important;transition:all 0.2s ease!important;width:100%;}
.stButton>button:hover{background:var(--rust-light)!important;transform:translateY(-1px)!important;box-shadow:0 5px 18px rgba(184,92,44,0.45)!important;}

.result-card{background:white;border-radius:var(--radius-lg);border:1px solid var(--warm-tan);padding:1.4rem 1.6rem;margin-bottom:1.2rem;box-shadow:var(--shadow-sm);}
.result-card-header{display:flex;align-items:center;gap:0.6rem;margin-bottom:0.9rem;padding-bottom:0.7rem;border-bottom:2px solid var(--parchment);}
.result-card-header h3{font-family:'Lora',serif;font-size:1rem;font-weight:600;color:var(--ink);margin:0;}
.result-card.answer{border-left:4px solid var(--forest);}
.result-card.explanation{border-left:4px solid var(--blue-ink);}
.result-card.conf-card{border-left:4px solid var(--gold);}
.result-card.context-card{border-left:4px solid var(--rust);}
.result-card.routing-card{border-left:4px solid var(--gold);}
.result-card.hitl-card{border-left:4px solid #e05252;background:#fffaf9;}

.confidence-bar-wrap{background:var(--parchment);border-radius:999px;height:12px;overflow:hidden;margin-top:0.5rem;}
.confidence-bar-fill{height:100%;border-radius:999px;}
.conf-high{background:linear-gradient(90deg,#2d5a3d,#4a7c5f);}
.conf-mid{background:linear-gradient(90deg,#c9943a,#e0b860);}
.conf-low{background:linear-gradient(90deg,#b85c2c,#d4784a);}
.confidence-label{font-family:'JetBrains Mono',monospace;font-size:0.83rem;margin-top:0.4rem;}

.conf-badge{display:inline-block;padding:0.18rem 0.6rem;border-radius:999px;font-size:0.75rem;font-weight:700;font-family:'JetBrains Mono',monospace;}
.conf-badge.high{background:rgba(45,90,61,0.12);color:#2d5a3d;}
.conf-badge.mid{background:rgba(201,148,58,0.15);color:#8a6520;}
.conf-badge.low{background:rgba(184,92,44,0.15);color:#b85c2c;}

.source-chip{display:inline-flex;align-items:center;gap:0.3rem;background:var(--parchment);border:1px solid var(--warm-tan);border-radius:6px;padding:0.25rem 0.6rem;font-size:0.78rem;font-family:'JetBrains Mono',monospace;color:var(--ink-muted);margin:0 0.3rem 0.3rem 0;}

.agent-step{display:flex;align-items:center;gap:0.7rem;padding:0.5rem 0.8rem;border-radius:8px;margin-bottom:0.35rem;font-size:0.85rem;transition:all 0.3s ease;}
.agent-step.pending{background:rgba(255,255,255,0.04);color:rgba(250,248,243,0.3);}
.agent-step.active{background:rgba(201,148,58,0.18);color:#e0b860;animation:pulse-step 1.2s ease-in-out infinite;}
.agent-step.done{background:rgba(45,90,61,0.22);color:#7ec99a;}
@keyframes pulse-step{0%,100%{opacity:1}50%{opacity:0.6}}
.step-dot{width:7px;height:7px;border-radius:50%;flex-shrink:0;}
.step-dot.pending{background:rgba(250,248,243,0.18);}
.step-dot.active{background:#c9943a;box-shadow:0 0 6px #c9943a;}
.step-dot.done{background:#7ec99a;}

.sidebar-hist-item{background:rgba(255,255,255,0.06);border:1px solid rgba(232,220,200,0.15);border-radius:8px;padding:0.6rem 0.85rem;margin-bottom:0.5rem;transition:all 0.18s ease;}
.sidebar-hist-item:hover{background:rgba(255,255,255,0.1);border-color:rgba(184,92,44,0.5);}
.sidebar-hist-q{font-size:0.82rem;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.sidebar-hist-c{font-size:0.74rem;font-family:'JetBrains Mono',monospace;margin-top:0.2rem;opacity:0.6;}

.memory-badge{display:inline-flex;align-items:center;gap:0.4rem;background:rgba(45,90,61,0.08);border:1px solid #4a7c5f;color:var(--forest);border-radius:999px;padding:0.28rem 0.85rem;font-size:0.8rem;font-weight:600;margin-bottom:0.8rem;}
.hitl-banner{background:#fff3f0;border:2px solid #e05252;border-radius:var(--radius-lg);padding:1rem 1.3rem;margin-bottom:1rem;}
.hitl-banner h4{color:#c0392b;font-family:'Lora',serif;margin:0 0 0.4rem;}
.ornamental-divider{text-align:center;color:var(--ink-faint);letter-spacing:0.5em;margin:1.2rem 0;}
.math-block{background:var(--parchment);border-radius:var(--radius);padding:1rem 1.3rem;font-family:'JetBrains Mono',monospace;font-size:0.95rem;color:var(--forest);border:1px solid var(--warm-tan);overflow-x:auto;}
::-webkit-scrollbar{width:6px;height:6px;}
::-webkit-scrollbar-track{background:var(--parchment);}
::-webkit-scrollbar-thumb{background:var(--warm-tan);border-radius:3px;}
</style>
""", unsafe_allow_html=True)

# ── Floating sidebar reopen button (JS) ──
st.markdown("""
<script>
(function(){
  function injectToggle(){
    var old=document.getElementById('sb-reopen-btn'); if(old) old.remove();
    var btn=document.createElement('button');
    btn.id='sb-reopen-btn'; btn.className='sidebar-toggle-btn';
    btn.title='Open sidebar'; btn.innerHTML='&#9776; Panel';
    btn.addEventListener('click',function(){
      var ctrl=document.querySelector('[data-testid="collapsedControl"] button');
      if(ctrl){ctrl.click();return;}
      var ctrl2=document.querySelector('[data-testid="collapsedControl"]');
      if(ctrl2) ctrl2.click();
    });
    document.body.appendChild(btn);
    function upd(){
      var sb=document.querySelector('[data-testid="stSidebar"]'); if(!sb) return;
      var collapsed=sb.getAttribute('aria-expanded')==='false'||sb.offsetWidth<40;
      btn.style.display=collapsed?'block':'none';
    }
    upd();
    var sb=document.querySelector('[data-testid="stSidebar"]');
    if(sb) new MutationObserver(upd).observe(sb,{attributes:true,attributeFilter:['aria-expanded','class','style']});
    setInterval(upd,400);
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',injectToggle);
  else setTimeout(injectToggle,500);
})();
</script>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────
# Session state
# ──────────────────────────────────────────────────────────
AGENTS = ["Parser","Router","Retriever","Solver","Verifier","Explainer"]
AGENT_ICONS = {"Parser":"🔍","Router":"🔀","Retriever":"📚","Solver":"🧮","Verifier":"✅","Explainer":"💬"}

if "chat_history"  not in st.session_state: st.session_state.chat_history  = []
if "agent_states"  not in st.session_state: st.session_state.agent_states  = {a:"pending" for a in AGENTS}
if "last_result"   not in st.session_state: st.session_state.last_result   = None
if "input_conf"    not in st.session_state: st.session_state.input_conf    = None   # OCR/ASR confidence
if "hitl_trigger"  not in st.session_state: st.session_state.hitl_trigger  = None   # reason string

# ──────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📐 AI Math Mentor")
    st.markdown("<hr style='border-color:rgba(201,148,58,0.3);margin:0.5rem 0 1rem'/>", unsafe_allow_html=True)
    st.markdown("### Agent Pipeline")
    agent_trace_ph = st.empty()

    def render_agent_trace(states):
        html = ""
        for name, status in states.items():
            icon   = AGENT_ICONS.get(name, "•")
            suffix = "<span style='margin-left:auto;font-size:0.7rem;opacity:0.7'>●●●</span>" if status=="active" else \
                     "<span style='margin-left:auto;font-size:0.7rem'>✓</span>"               if status=="done"   else ""
            html  += f'<div class="agent-step {status}"><div class="step-dot {status}"></div>{icon} {name}{suffix}</div>'
        agent_trace_ph.markdown(html, unsafe_allow_html=True)

    render_agent_trace(st.session_state.agent_states)
    st.markdown("<hr style='border-color:rgba(201,148,58,0.25);margin:1rem 0'/>", unsafe_allow_html=True)
    st.markdown("### 🕘 History")

    history_rows = get_recent_history(limit=10)
    if history_rows:
        for item in history_rows:
            q_short    = (item["question"] or "")[:50]
            conf_pct   = int((item["confidence"] or 0.5) * 100)
            topic      = item.get("topic") or "—"
            conf_color = "#7ec99a" if conf_pct>=75 else ("#e0b860" if conf_pct>=50 else "#d4784a")
            st.markdown(f"""
            <div class="sidebar-hist-item">
                <div class="sidebar-hist-q">{q_short}</div>
                <div class="sidebar-hist-c" style="color:{conf_color}">
                    {topic} · conf: {conf_pct}%
                </div>
            </div>""", unsafe_allow_html=True)
        if st.button("🗑 Clear History", key="clear_hist"):
            st.session_state.chat_history = []
            st.rerun()
    else:
        st.markdown("<p style='font-size:0.8rem;color:rgba(250,248,243,0.3);font-style:italic'>No problems solved yet.</p>",
                    unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────
# Pipeline bar + Header
# ──────────────────────────────────────────────────────────
pipeline_ph = st.empty()

def render_pipeline(states):
    agents = list(states.keys())
    html   = '<div class="pipeline-bar"><span class="pipeline-bar-label">Pipeline</span>'
    for i, name in enumerate(agents):
        status = states[name]; icon = AGENT_ICONS.get(name,"•")
        html  += f'<div class="pipe-step {status}"><div class="pipe-dot {status}"></div>{icon} {name}</div>'
        if i < len(agents)-1: html += '<span class="pipe-arrow">›</span>'
    html += '</div>'
    pipeline_ph.markdown(html, unsafe_allow_html=True)

render_pipeline(st.session_state.agent_states)

st.markdown("""
<div class="page-header">
    <h1>📐 AI Math Mentor</h1>
    <p>Step-by-step solutions powered by a multi-agent reasoning pipeline</p>
</div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────
# INPUT SECTION
# ──────────────────────────────────────────────────────────
tab_text, tab_image, tab_audio = st.tabs(["✏️  Text", "🖼️  Image", "🎙️  Audio"])
question      = ""
input_type    = "text"
input_conf    = 1.0    # default full confidence for typed text

with tab_text:
    st.markdown("<br/>", unsafe_allow_html=True)
    question   = st.text_area("Enter your math question",
                    placeholder="e.g.  Solve for x:  3x² − 5x + 2 = 0",
                    height=120, key="text_input")
    input_type = "text"
    input_conf = 1.0

with tab_image:
    st.markdown("<br/>", unsafe_allow_html=True)
    img_file = st.file_uploader("Upload an image of your problem",
                    type=["png","jpg","jpeg"], key="img_upload")
    if img_file:
        input_type = "image"
        with open("temp.png","wb") as f: f.write(img_file.read())
        extracted, ocr_conf = extract_text_from_image("temp.png")
        input_conf = ocr_conf

        # OCR confidence indicator
        badge_cls = "high" if ocr_conf>=0.75 else ("mid" if ocr_conf>=0.5 else "low")
        st.markdown(
            f'<span class="conf-badge {badge_cls}">OCR confidence: {int(ocr_conf*100)}%</span>',
            unsafe_allow_html=True)

        if ocr_conf < 0.6:
            st.warning("⚠️ Low OCR confidence — please review and correct the extracted text before solving.")

        question  = st.text_area("Extracted Text (edit if needed)", extracted,
                        height=100, key="img_text")
        st.image("temp.png", use_column_width=True, caption="Uploaded image")

with tab_audio:
    st.markdown("<br/>", unsafe_allow_html=True)
    aud_file = st.file_uploader("Upload an audio file",
                    type=["wav","mp3","m4a"], key="aud_upload")
    if aud_file:
        input_type = "audio"
        with open("temp.wav","wb") as f: f.write(aud_file.read())
        transcript, asr_conf = transcribe_audio("temp.wav")
        input_conf = asr_conf

        badge_cls = "high" if asr_conf>=0.75 else ("mid" if asr_conf>=0.5 else "low")
        st.markdown(
            f'<span class="conf-badge {badge_cls}">ASR confidence: {int(asr_conf*100)}%</span>',
            unsafe_allow_html=True)

        if asr_conf < 0.6:
            st.warning("⚠️ Low transcription confidence — please review and correct the transcript before solving.")

        question = st.text_area("Transcript (edit if needed)", transcript,
                       height=100, key="aud_text")

st.markdown("<div style='margin-top:1rem'/>", unsafe_allow_html=True)
_, btn_col, _ = st.columns([2,1,2])
with btn_col:
    solve_clicked = st.button("🧮  Solve Problem", key="solve_btn")

st.markdown("<hr style='border:none;border-top:2px solid #e8dcc8;margin:1.6rem 0 1rem'/>",
            unsafe_allow_html=True)
result_area = st.empty()

# ──────────────────────────────────────────────────────────
# Helper: render LaTeX explanation
# ──────────────────────────────────────────────────────────
def render_explanation(explanation: str):
    text = explanation.replace("\r\n","\n").replace("\r","\n")
    text = re.sub(r'\\\[\s*(.*?)\s*\\\]',   r'BLOCKMATH:\1:ENDBLOCK', text, flags=re.DOTALL)
    text = re.sub(r'\$\$\s*(.*?)\s*\$\$',   r'BLOCKMATH:\1:ENDBLOCK', text, flags=re.DOTALL)
    text = re.sub(r'(?m)^\\\s*\n(.*?)\n\\\s*$', r'BLOCKMATH:\1:ENDBLOCK', text, flags=re.DOTALL)
    text = re.sub(r'\[\s*((?:[^\[\]]*(?:\\[a-zA-Z]+|=|\+|-|\^|_|\{|\})[^\[\]]*)+?)\s*\]',
                  r'BLOCKMATH:\1:ENDBLOCK', text, flags=re.DOTALL)
    text = re.sub(r'\\\(\s*(.*?)\s*\\\)', r'$\1$', text, flags=re.DOTALL)
    text = re.sub(r'\(\s*((?:[^()]*(?:\\[a-zA-Z]+|[\^_=])[^()]*)+?)\s*\)', r'$\1$', text, flags=re.DOTALL)
    parts = re.split(r'BLOCKMATH:(.*?):ENDBLOCK', text, flags=re.DOTALL)
    for i, part in enumerate(parts):
        part = part.strip()
        if not part: continue
        if i % 2 == 1: st.latex(part)
        else:           st.markdown(part)

# ──────────────────────────────────────────────────────────
# Helper: render full result
# ──────────────────────────────────────────────────────────
def render_results(result: dict):
    solution     = result.get("solution","")
    explanation  = result.get("explanation","")
    confidence   = float((result.get("verification") or {}).get("confidence", 0.5))
    ver_comment  = (result.get("verification") or {}).get("comment","")
    rag_result   = result.get("rag_result") or {}
    routing      = result.get("routing") or {}
    needs_hitl   = result.get("needs_hitl", False)

    conf_pct   = int(confidence*100)
    conf_class = "conf-high" if confidence>=0.75 else ("conf-mid" if confidence>=0.5 else "conf-low")
    conf_label = "High confidence" if confidence>=0.75 else ("Moderate confidence" if confidence>=0.5 else "Low — review recommended")
    conf_color = "var(--forest)" if confidence>=0.75 else ("var(--gold)" if confidence>=0.5 else "var(--rust)")

    # ── HITL banner ──
    if needs_hitl:
        reason = "Verifier confidence is low" if confidence < 0.6 else "Parser detected ambiguity"
        st.markdown(f"""
        <div class="hitl-banner">
            <h4>⚠️ Human Review Required</h4>
            <p style="margin:0;font-size:0.88rem;color:#7b2d2d">{reason}. Please review the solution below and submit a correction if needed.</p>
        </div>""", unsafe_allow_html=True)

    # ── Routing info ──
    if routing:
        topic    = routing.get("topic","—")
        subtopic = routing.get("subtopic","—")
        strategy = routing.get("strategy","—")
        st.markdown(f"""
        <div class="result-card routing-card">
            <div class="result-card-header"><span style="font-size:1.2rem">🔀</span><h3>Problem Classification</h3></div>
            <div style="display:flex;gap:1rem;flex-wrap:wrap;font-size:0.85rem;">
                <span><b>Topic:</b> {topic}</span>
                <span><b>Subtopic:</b> {subtopic}</span>
                <span><b>Strategy:</b> {strategy}</span>
            </div>
        </div>""", unsafe_allow_html=True)

    # ── RAG context panel ──
    sources = rag_result.get("sources", [])
    chunks  = rag_result.get("chunks", [])
    if sources:
        chips = "".join(f'<span class="source-chip">📄 {s}</span>' for s in sources)
        st.markdown(f"""
        <div class="result-card context-card">
            <div class="result-card-header"><span style="font-size:1.2rem">📚</span><h3>Retrieved Context</h3></div>
            <div style="margin-bottom:0.6rem">{chips}</div>
        </div>""", unsafe_allow_html=True)
        with st.expander("View retrieved knowledge chunks"):
            for chunk in chunks:
                st.markdown(f"**📄 {chunk['source']}**")
                st.markdown(f"```\n{chunk['text'][:600]}{'...' if len(chunk['text'])>600 else ''}\n```")

    # ── Final answer ──
    st.markdown('<div class="result-card answer"><div class="result-card-header"><span style="font-size:1.2rem">🎯</span><h3>Final Answer</h3></div></div>',
                unsafe_allow_html=True)
    if solution and any(kw in solution.lower() for kw in ["error","could not","failed","syntax","invalid"]):
        st.warning("⚠️ Solver issue — symbolic solver could not parse this. See explanation below.")
    elif solution:
        st.latex(solution)
    else:
        st.info("No solution returned.")

    # ── Explanation ──
    st.markdown('<div class="result-card explanation"><div class="result-card-header"><span style="font-size:1.2rem">📝</span><h3>Step-by-Step Explanation</h3></div></div>',
                unsafe_allow_html=True)
    render_explanation(explanation)

    # ── Confidence ──
    st.markdown(f"""
    <div class="result-card conf-card">
        <div class="result-card-header"><span style="font-size:1.2rem">📊</span><h3>Confidence Score</h3></div>
        {f'<p style="font-size:0.83rem;color:var(--ink-muted);margin:0 0 0.5rem">{ver_comment}</p>' if ver_comment else ''}
        <div class="confidence-bar-wrap">
            <div class="confidence-bar-fill {conf_class}" style="width:{conf_pct}%"></div>
        </div>
        <div class="confidence-label" style="color:{conf_color}">{conf_pct}% — {conf_label}</div>
    </div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────
# Helper: run pipeline with animated trace
# ──────────────────────────────────────────────────────────
def run_pipeline(q):
    states = {a:"pending" for a in AGENTS}
    # Animate each step lighting up
    for step in AGENTS:
        states[step] = "active"
        render_pipeline(states); render_agent_trace(states)
        time.sleep(0.18)
    result = graph.invoke({"question": q})
    for step in AGENTS:
        states[step] = "done"
    render_pipeline(states); render_agent_trace(states)
    st.session_state.agent_states = states
    return result

# ──────────────────────────────────────────────────────────
# Solve logic
# ──────────────────────────────────────────────────────────
if solve_clicked and question.strip():
    # Check if input confidence is low → show HITL warning before solving
    if input_conf < 0.6:
        st.session_state.hitl_trigger = f"Low {'OCR' if input_type=='image' else 'ASR'} confidence ({int(input_conf*100)}%). Review the extracted text above before proceeding."

    st.session_state.agent_states = {a:"pending" for a in AGENTS}
    render_pipeline(st.session_state.agent_states)
    render_agent_trace(st.session_state.agent_states)

    with result_area.container():
        with st.spinner("Solving..."):
            prev_solution, prev_context = get_similar_problem(question)
            if prev_solution:
                st.markdown('<span class="memory-badge">📚 Retrieved from memory</span>', unsafe_allow_html=True)
                st.markdown(f'''<div class="result-card answer"><div class="result-card-header"><span style="font-size:1.2rem">📖</span><h3>Recalled Answer</h3></div><div class="math-block">{prev_solution}</div></div>''',
                            unsafe_allow_html=True)
                if prev_context:
                    render_context_panel(prev_context)
                done = {a:"done" for a in AGENTS}
                render_pipeline(done); render_agent_trace(done)
                st.session_state.agent_states = done
            else:
                result      = run_pipeline(question)
                solution    = result.get("solution","")
                explanation = result.get("explanation","")
                verification= result.get("verification",{})
                confidence  = float(verification.get("confidence",0.5))
                routing     = result.get("routing",{})
                rag_result  = result.get("rag_result",{})
                needs_hitl  = result.get("needs_hitl", False)

                # Also trigger HITL if needs_clarification from parser
                if result.get("parsed",{}).get("needs_clarification"):
                    needs_hitl = True

                render_results(result)

                # Store with full context
                store_solution(
                    question      = question,
                    solution      = solution,
                    input_type    = input_type,
                    parsed_json   = json.dumps(result.get("parsed",{})),
                    topic         = routing.get("topic",""),
                    context       = rag_result.get("context","")[:500],
                    sources       = ", ".join(rag_result.get("sources",[])),
                    confidence    = confidence,
                    verifier_comment = verification.get("comment",""),
                )

                st.session_state.last_result = result
                st.session_state.chat_history.append({"question":question,"confidence":confidence})

                # ── HITL correction UI ──
                if needs_hitl or confidence < 0.6:
                    st.markdown("<div class='ornamental-divider'>· · ·</div>", unsafe_allow_html=True)
                    st.markdown("""
                    <div class="result-card hitl-card">
                        <div class="result-card-header"><span style="font-size:1.2rem">✏️</span><h3>Human Review</h3></div>
                    </div>""", unsafe_allow_html=True)
                    correction = st.text_area("Submit a correction (optional)", key="correction_input",
                                              placeholder="Enter the correct answer or solution here...")
                    if st.button("Submit Correction", key="submit_correction"):
                        store_solution(question, correction, feedback="human_corrected",
                                       input_type=input_type, confidence=1.0)
                        st.success("✅ Correction stored as a learning signal.")

                # ── Feedback ──
                st.markdown("<div class='ornamental-divider'>· · ·</div>", unsafe_allow_html=True)
                fc1, fc2 = st.columns(2)
                with fc1:
                    if st.button("👍  Mark Correct", key="mark_correct"):
                        store_solution(question, solution, feedback="correct",
                                       input_type=input_type, confidence=confidence)
                        st.success("Marked as correct!")
                with fc2:
                    feedback = st.text_input("Feedback note", placeholder="What was wrong?", key="feedback_input")
                    if st.button("👎  Mark Incorrect", key="mark_incorrect"):
                        store_solution(question, solution, feedback=feedback or "incorrect",
                                       input_type=input_type, confidence=confidence)
                        st.info("Feedback saved.")

elif solve_clicked and not question.strip():
    with result_area.container():
        st.warning("Please enter a math question first.")

elif st.session_state.last_result and not solve_clicked:
    with result_area.container():
        render_results(st.session_state.last_result)