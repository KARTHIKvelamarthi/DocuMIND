# memory_processor.py

from langchain_community.llms import Ollama

class MemoryProcessor:
    def __init__(self, model_name="mistral"):
        self.llm = Ollama(model=model_name)

    def extract_key_points(self, answer):
        if not answer:
            return ""

        prompt = f"""
Extract key points from the following answer as bullet points:

{answer}
"""

        return self.llm.invoke(prompt)