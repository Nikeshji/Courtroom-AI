from backend.llm import llm
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
