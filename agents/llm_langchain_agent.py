import os
import logging
import requests

from config import OLLAMA_API_URL
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnableLambda

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ------------------------------------------------------------
# Initialize the chat model
# ------------------------------------------------------------

_llm = ChatOllama(
    model="mistral",
    base_url=OLLAMA_API_URL,
    temperature=0
)


# ------------------------------------------------------------
# Tool: get Databricks pipeline runs
# ------------------------------------------------------------

@tool
def get_pipeline_runs(pipeline_id: str) -> str:
    """
    Retrieve the most recent events for a Databricks pipeline.

    Use this when the user asks about:
    - pipeline runs
    - pipeline execution history
    - pipeline status
    - recent pipeline activity

    The input must be the Databricks pipeline_id.
    """
    logger.info("Calling Databricks API for pipeline_id=%s", pipeline_id)

    databricks_host = os.getenv("DATABRICKS_HOST")
    databricks_token = os.getenv("DATABRICKS_TOKEN")

    if not databricks_host or not databricks_token:
        return (
            "Databricks credentials are missing. "
            "Please set DATABRICKS_HOST and DATABRICKS_TOKEN."
        )

    url = f"{databricks_host}/api/2.0/pipelines/{pipeline_id}/events"
    headers = {"Authorization": f"Bearer {databricks_token}"}

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.exception("Databricks request failed")
        return f"Error retrieving pipeline runs: {exc}"

    data = response.json()
    events = data.get("events", [])[:5]

    if not events:
        return f"No recent events found for pipeline {pipeline_id}."

    lines = []
    for event in events:
        timestamp = event.get("timestamp", "unknown_timestamp")
        event_type = event.get("event_type", "unknown_event")
        message = event.get("message", "no_message")
        lines.append(f"{timestamp} | {event_type} | {message}")

    return "\n".join(lines)


tools = [get_pipeline_runs]


# ------------------------------------------------------------
# Create the agent
# ------------------------------------------------------------

_agent = create_agent(
    model=_llm,
    tools=tools,
    system_prompt=(
        "You are a data platform assistant. "
        "You have access to tools for retrieving Databricks pipeline information. "
        "If the user asks about pipeline runs, pipeline history, recent activity, "
        "or pipeline status, use the appropriate tool. "
        "Do not invent run information. "
        "If the tool returns an error, explain it clearly."
    )
)


# ------------------------------------------------------------
# Slack formatting helper
# ------------------------------------------------------------

def add_robot(text: str) -> str:
    text = text.lstrip()
    if text.startswith("🤖"):
        return text
    return f"🤖 {text}"


# ------------------------------------------------------------
# Pipeline: agent → extract reply → add robot emoji
#
# The agent returns a dict with a "messages" key: a list of all messages
# exchanged during reasoning (user input, tool calls, tool results, final answer).
# [-1] grabs the last message in that list, which is always the agent's final answer.
#
# Without a pipeline you would invoke the agent directly and
# post-process the result manually:
#
#   result = _agent.invoke({"messages": [{"role": "user", "content": question}]})
#   reply = add_robot(result["messages"][-1].content)
# ------------------------------------------------------------

pipeline = (
    _agent
    | RunnableLambda(lambda r: add_robot(r["messages"][-1].content))
)


# ------------------------------------------------------------
# Main interface used by the Slack bot
# ------------------------------------------------------------

def ask_llm(question: str) -> str:
    logger.info("User question: %s", question)
    reply = pipeline.invoke({"messages": [{"role": "user", "content": question}]})
    logger.info("Agent reply: %s", reply)
    return reply
