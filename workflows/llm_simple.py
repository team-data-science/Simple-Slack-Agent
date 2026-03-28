import logging
from collections import deque

from config import OLLAMA_API_URL
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_ollama import ChatOllama

# ------------------------------------------------------------
# Logging setup
# ------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ------------------------------------------------------------
# Simple in-memory chat history
# ------------------------------------------------------------
# We keep the last 5 user/assistant turns.
# Since each turn has 2 messages, we store up to 10 messages.
#
# This keeps the code very explicit and avoids relying on
# older memory abstractions that are harder to find in the docs.
# ------------------------------------------------------------

_history = deque(maxlen=10)


# ------------------------------------------------------------
# Initialize chat model
# ------------------------------------------------------------
# ChatOllama is the modern chat-style Ollama interface.
# ------------------------------------------------------------

_llm = ChatOllama(
    model="mistral",
    base_url=OLLAMA_API_URL,
    temperature=0
)


# ------------------------------------------------------------
# Small transformation for Slack replies
# ------------------------------------------------------------

def add_robot(text: str) -> str:
    return f"🤖 {text}"


# ------------------------------------------------------------
# Build message list for the model
# ------------------------------------------------------------

def build_messages(question: str):
    """
    Create the message list sent to the model.

    Structure:
    - system instruction
    - recent conversation history
    - latest user message
    """
    messages = [
        SystemMessage(
            content=(
                "You are a helpful local AI assistant inside Slack. "
                "Answer clearly and briefly. "
                "If you do not know something, say so."
            )
        )
    ]

    messages.extend(_history)
    messages.append(HumanMessage(content=question))

    return messages


# ------------------------------------------------------------
# Main interface used by the Slack bot
# ------------------------------------------------------------

def ask_llm(question: str) -> str:
    """
    Send the user's question to the local Ollama chat model
    and return the final response.
    """
    logger.info(f"User question: {question}")

    messages = build_messages(question)

    # Helpful debug output so you can see what is sent
    logger.info("Sending %s messages to ChatOllama", len(messages))
    for idx, msg in enumerate(messages):
        logger.info("%s | %s | %s", idx, msg.__class__.__name__, msg.content)

    result = _llm.invoke(messages)

    # ChatOllama returns an AIMessage-like object
    reply = result.content if hasattr(result, "content") else str(result)

    # Save the turn into memory
    _history.append(HumanMessage(content=question))
    _history.append(AIMessage(content=reply))

    reply = add_robot(reply)

    logger.info(f"Assistant reply: {reply}")

    return reply