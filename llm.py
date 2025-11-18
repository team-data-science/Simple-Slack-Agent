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

# RunnableSequence that takes prompt and the llm. you could argue that this is overkill, 
# because it's just one step. But with this adding e.g. tranformation features is super easy.
_chain = RunnableSequence(_prompt, _llm)


def ask_llm(question: str) -> str:
    """
    Send the question to the LLM chain with memory and return the response.
    """
    # Prepare input and memory
    inputs = {"input": question}
    mem_vars = _memory.load_memory_variables(inputs)
    chain_inputs = {**mem_vars, **inputs}

    # Invoke the runnable sequence (options are: invoke, stream, batch)
    result = _chain.invoke(chain_inputs)

    # Extract reply - LangChain can return different shapes depending on the model wrapper:
    if isinstance(result, str):
        reply = result
    elif isinstance(result, dict):
        reply = result.get("output") or result.get("text") or next(iter(result.values()))
    else:
        reply = str(result)

    # Save converstaion context into memory
    try:
        _memory.save_context(chain_inputs, {"output": reply})
    except Exception:
        pass

    return reply