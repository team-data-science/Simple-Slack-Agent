import os
from config import OLLAMA_API_URL
from langchain_ollama import OllamaLLM
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables.base import RunnableSequence

# Initialize Ollama LLM with HTTP API base URL
_llm = OllamaLLM(model="mistral", base_url=OLLAMA_API_URL)

# Window memory: keep last 5 turns with proper prefixes
_memory = ConversationBufferWindowMemory(
    k=5,
    memory_key="chat_history",
    input_key="input",
    human_prefix="Human",
    ai_prefix="Assistant"
)

# Prompt template combining history and new input
_prompt = PromptTemplate.from_template(
    """{chat_history}
Human: {input}
Assistant:"""
)

# RunnableSequence with memory loaded per invocation
_chain = RunnableSequence(_prompt, _llm)


def ask_llm(question: str) -> str:
    """
    Send the question to the LLM chain with memory and return the response.
    """
    # Prepare input and memory
    inputs = {"input": question}
    mem_vars = _memory.load_memory_variables(inputs)
    chain_inputs = {**mem_vars, **inputs}

    # Invoke model
    result = _chain.invoke(chain_inputs)

    # Extract reply
    if isinstance(result, str):
        reply = result
    elif isinstance(result, dict):
        reply = result.get("output") or result.get("text") or next(iter(result.values()))
    else:
        reply = str(result)

    # Save context
    try:
        _memory.save_context(chain_inputs, {"output": reply})
    except Exception:
        pass

    return reply