import os
import yaml

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama3.1:8b")
DEFAULT_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

class Config:
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._load_config()
        return cls._instance
    
    @classmethod
    def _load_config(cls):
        config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                cls._config = yaml.safe_load(f)
        else:
            cls._config = {}
    
    def get_model(self, agent_name: str) -> str:
        agents = self._config.get("agents", {})
        if agent_name in agents:
            return agents[agent_name].get("model", DEFAULT_MODEL)
        return self._config.get("default_model", DEFAULT_MODEL)
    
    def get_provider(self, agent_name: str) -> str:
        agents = self._config.get("agents", {})
        if agent_name in agents:
            return agents[agent_name].get("provider", DEFAULT_PROVIDER)
        return self._config.get("default_provider", DEFAULT_PROVIDER)
    
    def get_max_tokens(self, agent_name: str) -> int:
        agents = self._config.get("agents", {})
        if agent_name in agents:
            return agents[agent_name].get("max_tokens", 2048)
        return 2048

config = Config()
