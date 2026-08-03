from backend.llm import llm
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
    
    lines = response.strip().split("\n")
    headline = lines[0].replace("#", "").replace("**", "").strip()
    report = "\n".join(lines[1:]).strip()
    
    return {
        "headline": headline,
        "report": report if report else response
    }