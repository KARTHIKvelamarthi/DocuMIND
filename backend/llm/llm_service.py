# backend/llm/llm_service.py
# Identical behaviour to base_pipeline/llm_chain.py.

from langchain_community.llms import Ollama


class LLMService:
    def __init__(self, model_name: str = "mistral"):
        self.llm = Ollama(model=model_name)

    def run(self, prompt: str) -> str:
        return self.llm.invoke(prompt)
