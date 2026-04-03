import os
import logging
import requests
from typing import TypedDict

from config import OLLAMA_API_URL
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END

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


# ============================================================
# STEP 1: Agent only (no LangGraph)
#
# This is the simplest approach. You call the agent directly
# and post-process the result yourself.
#
# Good for: single-step workflows with no orchestration needs.
# ============================================================

def ask_llm_simple(question: str) -> str:
    result = _agent.invoke({"messages": [{"role": "user", "content": question}]})
    reply = result["messages"][-1].content
    return add_robot(reply)


# ============================================================
# STEP 2: Agent + LangGraph
#
# Here we wrap the agent in a LangGraph graph. Each step is
# a named node. The graph defines the order of execution.
#
# Good for: multi-step workflows where you want to add more
# nodes (validation, formatting, routing, retries) without
# restructuring the code — just add a node and an edge.
# ============================================================


# ------------------------------------------------------------
# State: the data that flows through the graph.
# Every node reads from and writes to this shared state.
# ------------------------------------------------------------

class AgentState(TypedDict):
    question: str
    reply: str


# ------------------------------------------------------------
# Nodes: each node is one step in the pipeline.
# A node receives the current state and returns the fields
# it wants to update.
# ------------------------------------------------------------

def agent_node(state: AgentState) -> AgentState:
    result = _agent.invoke({"messages": [{"role": "user", "content": state["question"]}]})
    return {"reply": result["messages"][-1].content}


def format_node(state: AgentState) -> AgentState:
    text = state["reply"].lstrip()
    return {"reply": text if text.startswith("🤖") else f"🤖 {text}"}


# ------------------------------------------------------------
# Graph: wire the nodes together with edges.
#
# Current flow:  START → agent → format → END
#
# To add a new step, add a node and an edge:
#   graph.add_node("validate", validate_node)
#   graph.add_edge("agent", "validate")
#   graph.add_edge("validate", "format")
#
# For conditional routing (e.g. retry on error):
#   graph.add_conditional_edges("agent", should_retry, {
#       "yes": "agent",   # loop back
#       "no":  "format"   # continue
#   })
# ------------------------------------------------------------

graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("format", format_node)
graph.add_edge(START, "agent")
graph.add_edge("agent", "format")
graph.add_edge("format", END)

pipeline = graph.compile()


# ------------------------------------------------------------
# Main interface used by the Slack bot
# ------------------------------------------------------------

def ask_llm(question: str) -> str:
    logger.info("User question: %s", question)
    result = pipeline.invoke({"question": question, "reply": ""})
    reply = result["reply"]
    logger.info("Agent reply: %s", reply)
    return reply
