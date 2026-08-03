from backend.llm import llm
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
        prompt += f"\nDEFENSE ARGUMENTS TO REBUT:\n{defense_args}\n"
    
    prompt += f"""Write a persuasive {round_label.lower()} argument for the prosecution.
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