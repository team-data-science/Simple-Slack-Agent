import os
from langchain_ollama import OllamaLLM
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate

# Determine Ollama API URL: use host.docker.internal inside Docker, fallback to localhost
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://host.docker.internal:11434")

# Initialize LangChain components once
llm = OllamaLLM(model="mistral", base_url=OLLAMA_API_URL)
# Use a window memory to keep only last 5 turns, with matching prefixes
memory = ConversationBufferWindowMemory(
    k=5,
    memory_key="chat_history",
    input_key="input",
    human_prefix="Human",
    ai_prefix="Assistant"
)
prompt = PromptTemplate.from_template(
    """{chat_history}
Human: {input}
Assistant:"""
)
_chain = LLMChain(llm=llm, prompt=prompt, memory=memory)

def ask_llm(question: str) -> str:
    """
    Send the question to the LLM chain and return the response.
    """
    return _chain.run(input=question)