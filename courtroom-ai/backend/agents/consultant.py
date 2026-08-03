from backend.llm import llm
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