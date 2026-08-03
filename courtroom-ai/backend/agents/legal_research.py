from backend.llm import llm
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