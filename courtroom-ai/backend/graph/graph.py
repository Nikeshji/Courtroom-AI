from langgraph.graph import StateGraph, END
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