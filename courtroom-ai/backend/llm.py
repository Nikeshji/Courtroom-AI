import os
import json
from typing import Type
from pydantic import BaseModel
from dotenv import load_dotenv

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import ollama
except ImportError:
    ollama = None

load_dotenv()

class LLMCaller:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        self.mock_mode = os.getenv("MOCK_LLM", "false").lower() == "true"
        
        if self.provider == "groq" and OpenAI:
            api_key = os.getenv("GROQ_API_KEY")
            self.groq_client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self.groq_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        else:
            self.groq_client = None
    
    def call(self, prompt: str, model: str = None, max_tokens: int = 2048, temperature: float = 0.7) -> str:
        if self.mock_mode:
            return self._mock_response(prompt)
        
        if self.provider == "groq" and self.groq_client:
            return self._call_groq(prompt, model or self.groq_model, max_tokens, temperature)
        else:
            return self._call_ollama(prompt, model or "llama3.1:8b", max_tokens, temperature)
    
    def call_structured(self, prompt: str, schema: Type[BaseModel], model: str = None, max_tokens: int = 2048) -> BaseModel:
        if self.mock_mode:
            return schema()
        
        schema_json = schema.model_json_schema()
        structured_prompt = f"""{prompt}

You MUST respond with a JSON object that strictly follows this schema:
{json.dumps(schema_json, indent=2)}

Respond ONLY with valid JSON. No markdown, no explanations outside the JSON."""
        
        if self.provider == "groq" and self.groq_client:
            response = self._call_groq(structured_prompt, model or self.groq_model, max_tokens, 0.2)
        else:
            response = self._call_ollama(structured_prompt, model or "llama3.1:8b", max_tokens, 0.2)
        
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        
        try:
            data = json.loads(response)
            return schema(**data)
        except Exception as e:
            print(f"JSON parse error: {e}")
            print(f"Raw response: {response[:500]}")
            return schema()
    
    def _call_groq(self, prompt: str, model: str, max_tokens: int, temperature: float) -> str:
        response = self.groq_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def _call_ollama(self, prompt: str, model: str, max_tokens: int, temperature: float) -> str:
        if ollama is None:
            raise RuntimeError("Ollama package not installed. Run: pip install ollama")
        
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": temperature, "num_predict": max_tokens}
        )
        return response["message"]["content"]
    
    def _mock_response(self, prompt: str) -> str:
        if "case manager" in prompt.lower():
            return json.dumps({
                "accused": "Unknown accused",
                "victim": "Complainant",
                "offences": "Section 279 BNS (Rash Driving)",
                "allegation": "Vehicle crashed into shop and fled",
                "jurisdiction": "Local Police Station",
                "facts": ["Vehicle crashed into shop", "Driver fled scene"],
                "missing_information": ["Vehicle number", "Exact date and time"]
            })
        return "This is a mock response for testing purposes."

llm = LLMCaller()
