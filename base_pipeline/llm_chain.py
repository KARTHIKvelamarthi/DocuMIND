# llm_chain.py

from langchain_community.llms import Ollama

class LLMChainWrapper:
    def __init__(self, model_name="mistral"):
        self.llm = Ollama(model=model_name)

    def run(self, prompt):
        return self.llm.invoke(prompt)