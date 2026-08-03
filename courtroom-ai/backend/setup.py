import os

base = r"C:\Users\nikes\OneDrive\Desktop\Courtroom_AI\courtroom-ai"

files = {}

# ============================================
# 1. SHARED STATE
# ============================================
files[r"backend\graph\state.py"] = '''from typing import TypedDict, Optional, Any, Dict

class CourtState(TypedDict, total=False):
    complaint: str
    case_intake: Optional[Dict[str, Any]]
    entities: Optional[str]
    accused: Optional[str]
    victim: Optional[str]
    offence: Optional[str]
    facts: Optional[str]
    legal_research: Optional[Dict[str, Any]]
    laws: Optional[str]
    sections_applied: Optional[str]
    precedents: Optional[str]
    consultant: Optional[str]
    top_consultant: Optional[str]
    pros_r1: Optional[str]
    def_r1: Optional[str]
    pros_r2: Optional[str]
    def_r2: Optional[str]
    judge_verdict: Optional[Dict[str, Any]]
    verdict: Optional[str]
    verdict_short: Optional[str]
    confidence: Optional[int]
    reasoning: Optional[str]
    probable_punishment: Optional[str]
    headline: Optional[str]
    report: Optional[str]
    is_running: bool
    execution_times: Dict[str, float]
'''

# ============================================
# 2. CASE MANAGER AGENT
# ============================================
files[r"backend\agents\case_manager.py"] = '''from backend.llm import llm
from backend.config import config
from backend.agents.schemas import CaseIntake

def run_case_manager(state):
    complaint = state.get("complaint", "")
    
    prompt = f"""You are a Court Case Intake Officer. Read the following complaint and extract structured information.

COMPLAINT:
{complaint}

Instructions:
- Identify the accused (who did it)
- Identify the victim (who suffered)
- Identify likely offences under Indian law (BNS 2023)
- Summarize the core allegation
- Note jurisdiction
- List material facts
- List what information is MISSING that would be needed in court

Respond with structured data."""
    
    result = llm.call_structured(
        prompt=prompt,
        schema=CaseIntake,
        model=config.get_model("case_manager"),
        max_tokens=config.get_max_tokens("case_manager")
    )
    
    intake_dict = result.model_dump()
    
    return {
        "case_intake": intake_dict,
        "entities": f"Accused: {intake_dict.get('accused', 'Unknown')}; Victim: {intake_dict.get('victim', 'Unknown')}",
        "accused": intake_dict.get("accused"),
        "victim": intake_dict.get("victim"),
        "offence": intake_dict.get("offences"),
        "facts": "; ".join(intake_dict.get("facts", []))
    }
'''

# ============================================
# 3. LEGAL RESEARCH AGENT
# ============================================
files[r"backend\agents\legal_research.py"] = '''from backend.llm import llm
from backend.config import config
from backend.agents.schemas import LegalResearch

def run_legal_research(state):
    case_intake = state.get("case_intake", {})
    offences = case_intake.get("offences", "")
    facts = case_intake.get("facts", [])
    
    prompt = f"""You are a Legal Researcher specializing in Indian criminal law (Bharatiya Nyaya Sanhita 2023, Bharatiya Nagarik Suraksha Sanhita 2023, Bharatiya Sakshya Adhiniyam 2023).

CASE FACTS:
{chr(10).join(f"- {f}" for f in facts)}

LIKELY OFFENCES: {offences}

Your task:
1. Identify exact statutory sections that apply
2. Mention relevant precedents (case names, courts, years)
3. Note any evidentiary issues
4. Flag unsettled legal questions

Be precise. If uncertain, say so."""
    
    result = llm.call_structured(
        prompt=prompt,
        schema=LegalResearch,
        model=config.get_model("legal_research"),
        max_tokens=config.get_max_tokens("legal_research")
    )
    
    research_dict = result.model_dump()
    
    sections_str = ", ".join([f"{s.get('section')} ({s.get('act')})" for s in research_dict.get("applicable_sections", [])])
    precedents_str = "; ".join([f"{p.get('case_name')} ({p.get('court')}, {p.get('year')})" for p in research_dict.get("precedents", [])])
    
    return {
        "legal_research": research_dict,
        "laws": sections_str,
        "sections_applied": sections_str,
        "precedents": precedents_str
    }
'''

# ============================================
# 4. CONSULTANT AGENT
# ============================================
files[r"backend\agents\consultant.py"] = '''from backend.llm import llm
from backend.config import config

def run_consultant(state):
    case_intake = state.get("case_intake", {})
    
    prompt = f"""You are a senior legal consultant giving a quick strategic read.

CASE: {case_intake.get('allegation', 'Unknown')}
OFFENCES: {case_intake.get('offences', 'Unknown')}
FACTS: {chr(10).join(case_intake.get('facts', []))}

Provide a brief strategic assessment:
- How strong does the case look for prosecution?
- What are the biggest weaknesses?
- What should each side focus on?

Write 2-3 paragraphs of free-form prose."""
    
    response = llm.call(
        prompt=prompt,
        model=config.get_model("consultant"),
        max_tokens=config.get_max_tokens("consultant")
    )
    
    return {"consultant": response}
'''

# ============================================
# 5. PROSECUTOR AGENT
# ============================================
files[r"backend\agents\prosecutor.py"] = '''from backend.llm import llm
from backend.config import config

def _build_prosecutor_prompt(state, round_num, is_closing=False):
    case_intake = state.get("case_intake", {})
    consultant = state.get("consultant", "")
    
    defense_args = ""
    if round_num == 2:
        defense_args = state.get("def_r1", "No defense argument yet.")
    
    round_label = "CLOSING" if is_closing else "OPENING"
    
    prompt = f"""You are a Public Prosecutor in an Indian criminal court. This is your {round_label} ARGUMENT (Round {round_num}).

CASE: {case_intake.get('allegation', '')}
FACTS: {chr(10).join(case_intake.get('facts', []))}
APPLICABLE LAWS: {state.get('laws', '')}

INTERNAL STRATEGY NOTE: {consultant}
"""
    
    if defense_args:
        prompt += f"\\nDEFENSE ARGUMENTS TO REBUT:\\n{defense_args}\\n"
    
    prompt += f"""
Write a persuasive {round_label.lower()} argument for the prosecution.
- Establish the facts clearly
- Apply the relevant sections of Bharatiya Nyaya Sanhita 2023
- Address weaknesses head-on
- Argue why the accused should be found guilty

Write as a real courtroom advocate would speak. 3-4 paragraphs."""
    
    return prompt

def run_prosecutor_r1(state):
    prompt = _build_prosecutor_prompt(state, 1, is_closing=False)
    response = llm.call(prompt=prompt, model=config.get_model("prosecutor"))
    return {"pros_r1": response}

def run_prosecutor_r2(state):
    prompt = _build_prosecutor_prompt(state, 2, is_closing=True)
    response = llm.call(prompt=prompt, model=config.get_model("prosecutor"))
    return {"pros_r2": response}
'''

# ============================================
# 6. DEFENSE AGENT
# ============================================
files[r"backend\agents\defense.py"] = '''from backend.llm import llm
from backend.config import config

def _build_defense_prompt(state, round_num, is_closing=False):
    case_intake = state.get("case_intake", {})
    
    pros_args = state.get("pros_r1" if round_num == 1 else "pros_r2", "")
    
    round_label = "CLOSING" if is_closing else "OPENING"
    
    prompt = f"""You are a Defense Advocate in an Indian criminal court. This is your {round_label} ARGUMENT (Round {round_num}).

CASE: {case_intake.get('allegation', '')}
FACTS: {chr(10).join(case_intake.get('facts', []))}
APPLICABLE LAWS: {state.get('laws', '')}

PROSECUTION ARGUMENTS TO REBUT:
{pros_args}

Write a persuasive {round_label.lower()} argument for the defense.
- Challenge the facts where they are weak
- Question the applicability of cited sections
- Raise reasonable doubt
- Argue why the accused should be acquitted

Write as a real defense lawyer would speak. 3-4 paragraphs."""
    
    return prompt

def run_defense_r1(state):
    prompt = _build_defense_prompt(state, 1, is_closing=False)
    response = llm.call(prompt=prompt, model=config.get_model("defense"))
    return {"def_r1": response}

def run_defense_r2(state):
    prompt = _build_defense_prompt(state, 2, is_closing=True)
    response = llm.call(prompt=prompt, model=config.get_model("defense"))
    return {"def_r2": response}
'''

# ============================================
# 7. JUDGE AGENT
# ============================================
files[r"backend\agents\judge.py"] = '''from backend.llm import llm
from backend.config import config
from backend.agents.schemas import JudgeVerdict

def run_judge(state):
    case_intake = state.get("case_intake", {})
    
    prompt = f"""You are a Judge in an Indian criminal court. You have heard all arguments. Deliver your verdict.

CASE FACTS:
{chr(10).join(case_intake.get('facts', []))}

PROSECUTION OPENING:
{state.get('pros_r1', '')}

DEFENSE OPENING:
{state.get('def_r1', '')}

PROSECUTION CLOSING:
{state.get('pros_r2', '')}

DEFENSE CLOSING:
{state.get('def_r2', '')}

APPLICABLE LAWS:
{state.get('laws', '')}

Your task:
1. State verdict: Guilty / Not Guilty / Partially Liable
2. Give confidence score (0-100)
3. Summarize key findings of fact
4. Assess prosecution arguments
5. Assess defense arguments
6. Provide full legal reasoning
7. List sections applied
8. State probable punishment

Be balanced. Acknowledge uncertainty where it exists."""
    
    result = llm.call_structured(
        prompt=prompt,
        schema=JudgeVerdict,
        model=config.get_model("judge"),
        max_tokens=config.get_max_tokens("judge")
    )
    
    verdict_dict = result.model_dump()
    
    return {
        "judge_verdict": verdict_dict,
        "verdict_short": verdict_dict.get("verdict"),
        "confidence": verdict_dict.get("confidence"),
        "verdict": verdict_dict.get("reasoning"),
        "reasoning": verdict_dict.get("reasoning"),
        "probable_punishment": verdict_dict.get("probable_punishment")
    }
'''

# ============================================
# 8. REPORTER AGENT
# ============================================
files[r"backend\agents\reporter.py"] = '''from backend.llm import llm
from backend.config import config

def run_reporter(state):
    verdict = state.get("judge_verdict", {})
    
    prompt = f"""You are a Court Reporter. Write a polished news-style report on this case.

VERDICT: {verdict.get('verdict', 'Unknown')}
CONFIDENCE: {verdict.get('confidence', 'N/A')}%
REASONING: {verdict.get('reasoning', '')}
PUNISHMENT: {verdict.get('probable_punishment', '')}

Write:
1. A compelling headline (one line)
2. A full report (4-5 paragraphs) summarizing the case, arguments, and verdict for a general audience.

Make it readable and professional."""
    
    response = llm.call(prompt=prompt, model=config.get_model("reporter"))
    
    lines = response.strip().split("\\n")
    headline = lines[0].replace("#", "").replace("**", "").strip()
    report = "\\n".join(lines[1:]).strip()
    
    return {
        "headline": headline,
        "report": report if report else response
    }
'''

# ============================================
# 9. TOP CONSULTANT AGENT
# ============================================
files[r"backend\agents\top_consultant.py"] = '''from backend.llm import llm
from backend.config import config

def run_top_consultant(state):
    prompt = f"""You are a Senior Legal Consultant reviewing a completed case file.

CASE: {state.get('case_intake', {}).get('allegation', '')}
VERDICT: {state.get('verdict_short', '')}
CONFIDENCE: {state.get('confidence', '')}%

Provide a closing strategic assessment:
- Was the verdict sound?
- What were the turning points?
- What could each side have done better?
- Any broader legal implications?

Write 2-3 paragraphs of executive-level analysis."""
    
    response = llm.call(prompt=prompt, model=config.get_model("top_consultant"))
    return {"top_consultant": response}
'''

# ============================================
# 10. WEB SEARCH PLACEHOLDER
# ============================================
files[r"backend\agents\web_search.py"] = '''# Placeholder for Tavily web search integration
# For now, Legal Research works without live search

def search_legal(query: str) -> str:
    return ""
'''

# ============================================
# 11. GRAPH WIRING
# ============================================
files[r"backend\graph\graph.py"] = '''from langgraph.graph import StateGraph, END
from backend.graph.state import CourtState

from backend.agents.case_manager import run_case_manager
from backend.agents.legal_research import run_legal_research
from backend.agents.consultant import run_consultant
from backend.agents.prosecutor import run_prosecutor_r1, run_prosecutor_r2
from backend.agents.defense import run_defense_r1, run_defense_r2
from backend.agents.judge import run_judge
from backend.agents.reporter import run_reporter
from backend.agents.top_consultant import run_top_consultant

def build_graph():
    workflow = StateGraph(CourtState)
    
    workflow.add_node("case_manager", run_case_manager)
    workflow.add_node("legal_research", run_legal_research)
    workflow.add_node("consultant", run_consultant)
    workflow.add_node("prosecutor_r1", run_prosecutor_r1)
    workflow.add_node("defense_r1", run_defense_r1)
    workflow.add_node("prosecutor_r2", run_prosecutor_r2)
    workflow.add_node("defense_r2", run_defense_r2)
    workflow.add_node("judge", run_judge)
    workflow.add_node("reporter", run_reporter)
    workflow.add_node("top_consultant", run_top_consultant)
    
    workflow.set_entry_point("case_manager")
    workflow.add_edge("case_manager", "legal_research")
    workflow.add_edge("legal_research", "consultant")
    workflow.add_edge("consultant", "prosecutor_r1")
    workflow.add_edge("prosecutor_r1", "defense_r1")
    workflow.add_edge("defense_r1", "prosecutor_r2")
    workflow.add_edge("prosecutor_r2", "defense_r2")
    workflow.add_edge("defense_r2", "judge")
    workflow.add_edge("judge", "reporter")
    workflow.add_edge("reporter", "top_consultant")
    workflow.add_edge("top_consultant", END)
    
    return workflow.compile()
'''

# ============================================
# 12. FASTAPI SERVER
# ============================================
files[r"backend\main.py"] = '''import os
import json
import time
import queue
import asyncio
import threading
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.graph.graph import build_graph
from backend.graph.state import CourtState

app = FastAPI(title="Courtroom AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

court_graph = build_graph()

class SimulateRequest(BaseModel):
    complaint: str

@app.get("/health")
def health_check():
    return {"ok": True, "message": "Backend is running"}

@app.post("/simulate/full")
async def simulate_full(request: SimulateRequest):
    initial_state: CourtState = {
        "complaint": request.complaint,
        "is_running": True,
        "execution_times": {}
    }
    
    def run_graph():
        return court_graph.invoke(initial_state)
    
    final_state = await asyncio.to_thread(run_graph)
    return final_state

@app.post("/simulate")
async def simulate_stream(request: SimulateRequest):
    initial_state: CourtState = {
        "complaint": request.complaint,
        "is_running": True,
        "execution_times": {}
    }
    
    async def event_generator() -> AsyncGenerator[str, None]:
        q = queue.Queue()
        start_time = time.time()
        
        def run_graph_in_thread():
            try:
                for node_output in court_graph.stream(initial_state):
                    elapsed = time.time() - start_time
                    for node_name in node_output:
                        node_output[node_name]["_elapsed"] = elapsed
                    q.put(("agent", node_output))
                q.put(("done", {}))
            except Exception as e:
                q.put(("error", {"error": str(e)}))
        
        thread = threading.Thread(target=run_graph_in_thread, daemon=True)
        thread.start()
        
        while True:
            try:
                event_type, data = await asyncio.to_thread(q.get, timeout=300)
                
                if event_type == "done":
                    yield f"event: done\\ndata: {json.dumps({'status': 'complete'})}\\n\\n"
                    break
                elif event_type == "error":
                    yield f"event: error\\ndata: {json.dumps(data)}\\n\\n"
                    break
                elif event_type == "agent":
                    yield f"event: agent\\ndata: {json.dumps(data)}\\n\\n"
                    
            except queue.Empty:
                yield f"event: error\\ndata: {json.dumps({'error': 'Timeout'})}\\n\\n"
                break
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

# Write all files
for path, content in files.items():
    full_path = os.path.join(base, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created: {full_path}")

print("\nAll backend files created successfully!")