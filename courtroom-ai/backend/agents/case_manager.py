from backend.llm import llm
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