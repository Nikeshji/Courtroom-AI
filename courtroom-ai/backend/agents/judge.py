from backend.llm import llm
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