from backend.llm import llm
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