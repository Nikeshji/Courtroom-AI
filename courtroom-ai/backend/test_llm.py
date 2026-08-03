from llm import llm
from agents.schemas import CaseIntake

print("=== Test 1: Simple text call ===")
response = llm.call("Say 'Hello from Courtroom AI' in one sentence.")
print(response)
print()

print("=== Test 2: Structured JSON call ===")
prompt = """You are a Court Case Intake Officer. Extract structured info from this complaint:
"Someone stole my phone from my bag in the metro."
"""
result = llm.call_structured(prompt, CaseIntake)
print(result)
print()

print("If you see both responses above, your LLM connection is working!")
