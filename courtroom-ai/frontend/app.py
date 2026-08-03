import os
import json
import time
import textwrap
import io
import requests
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from evaluation.evaluator import SystemEvaluator
from evaluation.dashboard import show_evaluation_dashboard

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Courtroom AI", page_icon="⚖️", layout="wide")

# ==================== CSS ====================
st.markdown("""
<style>
.stApp { background: #F5F9FF !important; font-family: 'Inter', sans-serif; }
.court-header {
    background: linear-gradient(135deg, #D4E8FF 0%, #FFE0ED 100%);
    padding: 1.5rem; border-bottom: 3px solid #FFB6C1;
    margin-bottom: 1.5rem; text-align: center;
    border-radius: 0 0 24px 24px;
}
.court-header h1 { font-size: 28px; color: #2A4B7C; margin: 0; }
.court-header span { color: #B85C7A; background: rgba(255,182,193,0.25); padding: 2px 12px; border-radius: 40px; }
.judge-bench {
    background: linear-gradient(180deg, #2A4B7C 0%, #1E3A5F 100%);
    color: white; padding: 1.2rem; border-radius: 16px;
    text-align: center; border: 3px solid #FFB6C1;
    box-shadow: 0 8px 24px rgba(42,75,124,0.3);
}
.judge-avatar { font-size: 56px; margin-bottom: 4px; }
.verdict-guilty { color: #f87171; font-size: 24px; font-weight: 800; }
.verdict-not-guilty { color: #4ade80; font-size: 24px; font-weight: 800; }
.verdict-partial { color: #fbbf24; font-size: 24px; font-weight: 800; }
.lawyer-card {
    background: white; border-radius: 16px; padding: 1rem;
    border-top: 4px solid; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    height: 100%;
}
.prosecution-border { border-top-color: #A8D8EA; }
.defense-border { border-top-color: #FFB6C1; }
.research-box {
    background: white; border-radius: 12px; padding: 1rem;
    border: 1px solid #E6EDFF; text-align: center;
}
.speech-bubble {
    background: #F8FAFF; border-left: 4px solid; padding: 0.8rem 1rem;
    margin-bottom: 0.6rem; border-radius: 0 10px 10px 0;
    font-size: 13px; line-height: 1.7; color: #1E2937;
}
.pros-bubble { border-left-color: #A8D8EA; }
.def-bubble { border-left-color: #FFB6C1; }
.clerk-card {
    background: white; border: 2px solid #E6EDFF;
    border-radius: 14px; padding: 1rem 1.5rem;
    max-width: 500px; margin: 0 auto;
}
.reporter-desk {
    background: white; border: 1px solid #E6EDFF;
    border-top: 4px solid #A8D8EA; border-radius: 16px;
    padding: 1.2rem 1.5rem;
}
.gold-divider {
    height: 2px; background: linear-gradient(90deg, transparent, #FFB6C1, transparent);
    margin: 1rem 0; opacity: 0.6;
}
.status-pill {
    display: inline-block; background: #F8FAFF;
    border: 1px solid #FFE0ED; color: #B85C7A;
    padding: 4px 16px; border-radius: 30px;
    font-size: 12px; font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

import html as _html_module
def esc(text) -> str:
    if text is None: return ""
    return _html_module.escape(str(text))

def _parse_sse_stream(response):
    event, data = None, None
    for raw_line in response.iter_lines(decode_unicode=True):
        if raw_line is None: continue
        line = raw_line.strip()
        if line == "":
            if event and data is not None: yield event, data
            event, data = None, None
            continue
        if line.startswith("event:"): event = line[len("event:"):].strip()
        elif line.startswith("data:"): data = line[len("data:"):].strip()
    if event and data is not None: yield event, data

def _build_report_content(state: dict) -> str:
    lines = []
    lines.append("# ⚖️ Courtroom AI Simulation Report")
    lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(""); lines.append("## 🏛️ Top Consultant")
    lines.append(state.get('top_consultant','Not available.') or 'Not available.')
    lines.append(""); lines.append("## ⚔️ Prosecution Round 1")
    lines.append(state.get('pros_r1','Not available.') or 'Not available.')
    lines.append(""); lines.append("## 🛡️ Defense Round 1")
    lines.append(state.get('def_r1','Not available.') or 'Not available.')
    lines.append(""); lines.append("## ⚔️ Prosecution Round 2")
    lines.append(state.get('pros_r2','Not available.') or 'Not available.')
    lines.append(""); lines.append("## 🛡️ Defense Round 2")
    lines.append(state.get('def_r2','Not available.') or 'Not available.')
    lines.append(""); lines.append("## 👨‍⚖️ Judge")
    jv = state.get("judge_verdict")
    if jv:
        lines.append(f"- **Verdict:** {jv.get('verdict','Unknown')}")
        lines.append(f"- **Confidence:** {jv.get('confidence','N/A')}%")
        lines.append(f"- **Reasoning:** {jv.get('reasoning','')}")
        lines.append(f"- **Sections:** {', '.join(jv.get('sections_applied',[]))}")
        lines.append(f"- **Punishment:** {jv.get('probable_punishment','')}")
    lines.append(""); lines.append("## 📰 Reporter")
    lines.append(f"- **Headline:** {state.get('headline','No headline.')}")
    lines.append(f"- **Report:**\n{state.get('report','Not available.')}")
    lines.append(""); lines.append("## 📂 Case Manager")
    ci = state.get("case_intake")
    if ci:
        lines.append(f"- **Accused:** {ci.get('accused','Unknown')}")
        lines.append(f"- **Victim:** {ci.get('victim','Unknown')}")
        lines.append(f"- **Offences:** {ci.get('offences','Unknown')}")
    return "\n".join(lines)

def _build_pdf_bytes(report_text: str) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    left, top, line_height = 50, height - 50, 12

    def draw_wrapped(text, x, y, font_name="Helvetica", font_size=10):
        c.setFont(font_name, font_size)
        text = text.replace("**","")
        for raw_line in text.split("\n"):
            if y < 50:
                c.showPage(); c.setFont(font_name, font_size); y = height - 50
            if not raw_line.strip(): y -= line_height; continue
            for chunk in textwrap.wrap(raw_line, width=110):
                if y < 50: c.showPage(); c.setFont(font_name, font_size); y = height - 50
                c.drawString(x, y, chunk); y -= line_height
        return y

    y = top
    for line in report_text.splitlines():
        if y < 50: c.showPage(); y = height - 50
        if line.startswith("# "): y = draw_wrapped(line[2:], left, y, "Helvetica-Bold", 16); y -= 6
        elif line.startswith("## "): y = draw_wrapped(line[3:], left, y, "Helvetica-Bold", 12); y -= 4
        else: y = draw_wrapped(line, left, y)
    c.save()
    return buffer.getvalue()

EMPTY_CASE_STATE = {
    "complaint": "", "entities": None, "accused": None, "victim": None,
    "offence": None, "facts": None, "case_intake": None,
    "laws": None, "sections_applied": None, "precedents": None,
    "legal_research": None, "consultant": None, "top_consultant": None,
    "pros_r1": None, "def_r1": None, "pros_r2": None, "def_r2": None,
    "verdict": None, "verdict_short": None, "confidence": None,
    "reasoning": None, "probable_punishment": None, "judge_verdict": None,
    "headline": None, "report": None, "is_running": False, "execution_times": {},
}

for key, val in [
    ("case_state", dict(EMPTY_CASE_STATE)),
    ("simulation_complete", False),
    ("stream_event_generator", None),
    ("node_times", {}),
    ("evaluator", SystemEvaluator()),
    ("metrics_recorded", False),
    ("last_metrics", None),
    ("simulation_error", None),
]:
    if key not in st.session_state: st.session_state[key] = val

# ==================== HEADER ====================
st.markdown("""
<div class="court-header">
    <h1>⚖️ <span>COURTROOM</span> AI</h1>
    <p>Indian Law · Multi-Agent Adversarial Simulation</p>
</div>
""", unsafe_allow_html=True)

try:
    health = requests.get(f"{BACKEND_URL}/health", timeout=5).json()
    if not health.get("ok"): st.error("Backend not ready"); st.stop()
except requests.exceptions.RequestException:
    st.error(f"Cannot reach backend at {BACKEND_URL}. Is it running? (`uvicorn backend.main:app --reload`)"); st.stop()

tab_simulation, tab_metrics = st.tabs(["⚖️ Courtroom", "📊 Metrics"])

with tab_simulation:
    # ----- INPUT -----
    if not st.session_state.case_state.get("is_running") and not st.session_state.simulation_complete:
        with st.container():
            c1, c2 = st.columns([3, 1])
            with c1:
                complaint = st.text_area("Complaint or case brief", height=100,
                    placeholder="Someone crashed into my shop and ran away...",
                    key="complaint_input")
            with c2:
                st.write(""); st.write("")
                if st.button("⚖️ Begin Simulation", type="primary", use_container_width=True):
                    current = st.session_state.get("complaint_input", "")
                    if not current.strip(): st.warning("Please enter a complaint."); st.stop()
                    st.session_state.case_state = dict(EMPTY_CASE_STATE)
                    st.session_state.case_state["complaint"] = current
                    st.session_state.case_state["is_running"] = True
                    st.session_state.simulation_complete = False
                    st.session_state.node_times = {}
                    st.session_state.metrics_recorded = False
                    st.session_state.last_metrics = None
                    st.session_state.simulation_error = None
                    st.session_state.stream_event_generator = None
                    try:
                        response = requests.post(f"{BACKEND_URL}/simulate", json={"complaint": current}, stream=True, timeout=300)
                        response.raise_for_status()
                        st.session_state.stream_event_generator = _parse_sse_stream(response)
                        st.session_state.sim_start_time = time.time()
                    except Exception as e:
                        st.error(f"Failed to start: {e}")
                        st.session_state.case_state["is_running"] = False
                        st.stop()
                    st.rerun()

    if st.session_state.simulation_error: st.error(f"❌ {st.session_state.simulation_error}")
    if st.session_state.case_state.get("is_running"):
        st.markdown('<div style="text-align:center;color:#94A3B8;font-size:13px;letter-spacing:1px;">⚖️ Court is in session... Arguments are being exchanged.</div>', unsafe_allow_html=True)
    elif st.session_state.simulation_complete:
        st.markdown('<div style="text-align:center;color:#94A3B8;font-size:13px;letter-spacing:1px;">✅ The Hon\'ble Judge has delivered the final verdict.</div>', unsafe_allow_html=True)

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    # ==================== COURTROOM FLOOR ====================
    s = st.session_state.case_state

    # --- JUDGE BENCH (Top Center) ---
    judge_verdict = s.get("judge_verdict")
    verdict_short = s.get("verdict_short")
    confidence = s.get("confidence")

    if verdict_short:
        vl = str(verdict_short).lower()
        if "not guilty" in vl: vcolor, vtext = "verdict-not-guilty", "NOT GUILTY"
        elif "partially" in vl: vcolor, vtext = "verdict-partial", "PARTIALLY LIABLE"
        elif "guilty" in vl: vcolor, vtext = "verdict-guilty", "GUILTY"
        else: vcolor, vtext = "verdict-partial", esc(verdict_short).upper()

        st.markdown(f"""
        <div class="judge-bench">
            <div class="judge-avatar">👨‍⚖️</div>
            <div style="font-size:11px;text-transform:uppercase;letter-spacing:2px;opacity:0.8;">The Hon'ble Judge</div>
            <div class="{vcolor}">{vtext}</div>
            <div style="margin-top:6px;"><span class="status-pill">Confidence {esc(confidence)}%</span></div>
            {f'<div style="margin-top:10px;font-size:13px;opacity:0.9;">{esc(judge_verdict.get("reasoning",""))[:200]}...</div>' if judge_verdict else ''}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="judge-bench">
            <div class="judge-avatar">👨‍⚖️</div>
            <div style="font-size:11px;text-transform:uppercase;letter-spacing:2px;opacity:0.8;">The Hon'ble Judge</div>
            <div style="font-size:16px;opacity:0.7;">Awaiting arguments...</div>
        </div>
        """, unsafe_allow_html=True)

    # --- COURT CLERK / CASE MANAGER ---
    case_intake = s.get("case_intake")
    st.markdown('<div style="margin-top:16px;">', unsafe_allow_html=True)
    if case_intake:
        st.markdown(f"""
        <div class="clerk-card">
            <div style="text-align:center;font-size:32px;margin-bottom:4px;">📂</div>
            <div style="text-align:center;color:#2A4B7C;font-size:11px;text-transform:uppercase;letter-spacing:2px;font-weight:700;margin-bottom:8px;">Case Manager — Court Clerk</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:13px;color:#1E2937;">
                <div><strong style="color:#2A4B7C;">Accused:</strong> {esc(case_intake.get('accused','Unknown'))}</div>
                <div><strong style="color:#2A4B7C;">Victim:</strong> {esc(case_intake.get('victim','Unknown'))}</div>
                <div><strong style="color:#2A4B7C;">Offence:</strong> {esc(case_intake.get('offences','Unknown'))}</div>
                <div><strong style="color:#2A4B7C;">Jurisdiction:</strong> {esc(case_intake.get('jurisdiction','Unknown'))}</div>
            </div>
            <div style="margin-top:8px;font-size:12px;color:#475569;"><strong>Allegation:</strong> {esc(case_intake.get('allegation',''))}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="clerk-card" style="text-align:center;color:#94A3B8;">
            <div style="font-size:32px;">📂</div>
            <div>Court Clerk is processing the complaint...</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- LAWYERS ROW ---
    col_pros, col_center, col_def = st.columns([2, 1.5, 2])

    with col_pros:
        st.markdown("""
        <div style="text-align:center;">
            <div style="font-size:48px;">⚔️</div>
            <div style="background:#A8D8EA;color:#2A4B7C;padding:4px 14px;border-radius:20px;font-weight:700;font-size:11px;display:inline-block;text-transform:uppercase;letter-spacing:1px;">Public Prosecutor</div>
        </div>
        """, unsafe_allow_html=True)
        r1 = s.get("pros_r1")
        if r1:
            st.markdown(f'<div class="speech-bubble pros-bubble"><div style="font-size:10px;text-transform:uppercase;color:#2A4B7C;font-weight:700;margin-bottom:4px;">Round 1 — Opening</div>{esc(r1)}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center;color:#94A3B8;font-size:13px;font-style:italic;padding:1rem;">Awaiting opening argument...</div>', unsafe_allow_html=True)

        r2 = s.get("pros_r2")
        if r2:
            st.markdown(f'<div class="speech-bubble pros-bubble"><div style="font-size:10px;text-transform:uppercase;color:#2A4B7C;font-weight:700;margin-bottom:4px;">Round 2 — Closing</div>{esc(r2)}</div>', unsafe_allow_html=True)

    with col_center:
        # Legal Research
        legal_research = s.get("legal_research")
        st.markdown('<div class="research-box" style="margin-bottom:12px;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:36px;">📚</div>', unsafe_allow_html=True)
        st.markdown('<div style="color:#B85C7A;font-size:10px;text-transform:uppercase;font-weight:700;letter-spacing:1px;">Legal Research</div>', unsafe_allow_html=True)
        if legal_research:
            sections = legal_research.get("applicable_sections") or []
            for sec in sections:
                st.markdown(f'<div style="background:#F8FAFF;border:1px solid #E6EDFF;border-radius:8px;padding:6px 10px;margin-top:6px;font-size:11px;"><strong style="color:#2A4B7C;">{esc(sec.get("section"))}</strong> <span style="color:#64748B;">({esc(sec.get("act"))})</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#94A3B8;font-size:11px;margin-top:4px;">Researching laws...</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Consultant
        consultant = s.get("consultant")
        st.markdown('<div class="research-box">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:36px;">🧭</div>', unsafe_allow_html=True)
        st.markdown('<div style="color:#2A4B7C;font-size:10px;text-transform:uppercase;font-weight:700;letter-spacing:1px;">Consultant</div>', unsafe_allow_html=True)
        if consultant:
            st.markdown(f'<div style="color:#475569;font-size:11px;margin-top:4px;text-align:left;">{esc(consultant)[:200]}...</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#94A3B8;font-size:11px;margin-top:4px;">Reviewing case...</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_def:
        st.markdown("""
        <div style="text-align:center;">
            <div style="font-size:48px;">🛡️</div>
            <div style="background:#FFB6C1;color:white;padding:4px 14px;border-radius:20px;font-weight:700;font-size:11px;display:inline-block;text-transform:uppercase;letter-spacing:1px;">Defense Advocate</div>
        </div>
        """, unsafe_allow_html=True)
        r1 = s.get("def_r1")
        if r1:
            st.markdown(f'<div class="speech-bubble def-bubble"><div style="font-size:10px;text-transform:uppercase;color:#B85C7A;font-weight:700;margin-bottom:4px;">Round 1 — Opening</div>{esc(r1)}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center;color:#94A3B8;font-size:13px;font-style:italic;padding:1rem;">Awaiting opening argument...</div>', unsafe_allow_html=True)

        r2 = s.get("def_r2")
        if r2:
            st.markdown(f'<div class="speech-bubble def-bubble"><div style="font-size:10px;text-transform:uppercase;color:#B85C7A;font-weight:700;margin-bottom:4px;">Round 2 — Closing</div>{esc(r2)}</div>', unsafe_allow_html=True)

    # --- REPORTER ---
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    headline = s.get("headline")
    report = s.get("report")
    if headline or report:
        st.markdown("""
        <div class="reporter-desk">
            <div style="text-align:center;font-size:40px;margin-bottom:4px;">📰</div>
            <div style="text-align:center;color:#2A4B7C;font-size:11px;text-transform:uppercase;font-weight:700;letter-spacing:2px;margin-bottom:10px;">Court Reporter</div>
        """, unsafe_allow_html=True)
        if headline:
            st.markdown(f'<div style="color:#2A4B7C;font-size:18px;font-weight:700;margin-bottom:10px;border-left:4px solid #FFB6C1;padding-left:12px;">📌 {esc(headline)}</div>', unsafe_allow_html=True)
        if report:
            st.markdown(f'<div style="color:#1E2937;font-size:14px;line-height:1.8;">{esc(report)}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TOP CONSULTANT ---
    top_consultant = s.get("top_consultant")
    if top_consultant or st.session_state.simulation_complete:
        st.markdown("""
        <div style="background:#F8FAFF;border:1px solid #FFE0ED;border-top:4px solid #FFB6C1;border-radius:16px;padding:1.2rem 1.5rem;margin-top:1rem;">
            <div style="text-align:center;font-size:32px;margin-bottom:4px;">🏛️</div>
            <div style="text-align:center;color:#B85C7A;font-size:11px;text-transform:uppercase;font-weight:700;letter-spacing:2px;margin-bottom:8px;">Senior Consultant</div>
        """, unsafe_allow_html=True)
        if top_consultant:
            st.markdown(f'<div style="color:#1E2937;font-size:14px;line-height:1.7;">{esc(top_consultant)}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#94A3B8;font-style:italic;text-align:center;">Reviewing the full case file...</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- STREAMING ENGINE ---
    if s.get("is_running") and not st.session_state.simulation_complete:
        progress = st.empty()
        progress.info("🔄 Streaming simulation events...")
        if st.session_state.stream_event_generator is not None:
            try:
                event_type, data = next(st.session_state.stream_event_generator)
                if event_type == "agent":
                    payload = json.loads(data)
                    for node_name, partial in payload.items():
                        elapsed = time.time() - st.session_state.sim_start_time
                        st.session_state.node_times[node_name] = elapsed
                        for key, value in partial.items():
                            if value is not None: st.session_state.case_state[key] = value
                    progress.info(f"🔄 Received: {', '.join(payload.keys())}")
                elif event_type == "error":
                    error_data = json.loads(data)
                    st.session_state.simulation_error = error_data.get("error", "Unknown error")
                    st.session_state.case_state["is_running"] = False
                    st.session_state.stream_event_generator = None
                    progress.error("❌ Simulation error"); st.rerun()
                elif event_type == "done":
                    st.session_state.simulation_complete = True
                    st.session_state.case_state["is_running"] = False
                    st.session_state.stream_event_generator = None
                    progress.success("✅ Simulation completed!")
                st.rerun()
            except StopIteration:
                st.session_state.simulation_error = "Stream ended unexpectedly."
                st.session_state.case_state["is_running"] = False
                st.session_state.stream_event_generator = None
                progress.error("❌ Simulation stopped unexpectedly."); st.rerun()
            except Exception as e:
                st.session_state.simulation_error = str(e)
                st.session_state.case_state["is_running"] = False
                st.session_state.stream_event_generator = None
                progress.error(f"❌ Unexpected error: {e}"); st.rerun()

    # --- IDLE STATE ---
    if not s.get("is_running") and not st.session_state.simulation_complete and not s.get("complaint"):
        st.markdown("""
        <div style="text-align:center;padding:4rem 1rem;color:#94A3B8;">
            <div style="font-size:64px;margin-bottom:1rem;">🏛️</div>
            <h2 style="color:#2A4B7C;font-weight:400;letter-spacing:2px;font-size:26px;">The Court Awaits</h2>
            <p style="font-size:15px;">Enter a case brief above to begin the adversarial simulation.</p>
        </div>
        """, unsafe_allow_html=True)

    # --- COMPLETE: DOWNLOADS ---
    if st.session_state.simulation_complete:
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        if not st.session_state.metrics_recorded:
            metrics = st.session_state.evaluator.evaluate_case(st.session_state.case_state, st.session_state.node_times)
            st.session_state.metrics_recorded = True
            st.session_state.last_metrics = metrics
            st.success(f"✅ Case evaluated. Quality Score: {metrics.overall_quality_score:.1f}/100")

        report_content = _build_report_content(st.session_state.case_state)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button("📄 Download PDF", _build_pdf_bytes(report_content), "courtroom_report.pdf", "application/pdf", use_container_width=True)
        with c2:
            st.download_button("📥 Download Markdown", report_content, "courtroom_report.md", "text/markdown", use_container_width=True)
        with c3:
            if st.button("🔄 Start New Case", use_container_width=True):
                st.session_state.case_state = dict(EMPTY_CASE_STATE)
                st.session_state.simulation_complete = False
                st.session_state.stream_event_generator = None
                st.session_state.node_times = {}
                st.session_state.metrics_recorded = False
                st.session_state.last_metrics = None
                st.session_state.simulation_error = None
                st.rerun()

with tab_metrics:
    show_evaluation_dashboard()