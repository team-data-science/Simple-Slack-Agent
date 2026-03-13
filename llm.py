# Run this query: show me the runs for databricks pipeline: pipline_id


import os
import logging
import requests

from config import OLLAMA_API_URL
from langchain_ollama import ChatOllama

# Tool decorator allows LangChain to expose a Python function
# to the LLM as something it can "call".
from langchain.tools import tool

# These classes create an agent that can decide which tool to call
from langchain.agents import create_tool_calling_agent, AgentExecutor

# ChatPromptTemplate is used for agents instead of the simple PromptTemplate
from langchain_core.prompts import ChatPromptTemplate


# ------------------------------------------------------------
# Logging setup
# ------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ------------------------------------------------------------
# Initialize the LLM
# ------------------------------------------------------------

# This connects LangChain to a local Ollama instance.
# In your case this runs Mistral locally.
_llm = ChatOllama(
    model="mistral",
    base_url=OLLAMA_API_URL,
    temperature=0
)


# ------------------------------------------------------------
# Define a TOOL the LLM can call
# ------------------------------------------------------------

# The @tool decorator registers the function as a tool
# that the LLM can decide to use.
#
# LangChain will automatically extract:
# - tool name
# - tool description
# - arguments
#
# and provide that information to the model.


@tool
def get_pipeline_runs(pipeline_id: str):
    """
    Retrieve the recent execution runs of a Databricks pipeline.

    Use this tool when a user asks about:
    - pipeline runs
    - pipeline execution history
    - pipeline status
    - recent pipeline activity

    The input must be the pipeline_id.
    """

    logger.info(f"Calling Databricks API for pipeline {pipeline_id}")

    # Example Databricks API endpoint
    # NOTE: replace with your real workspace URL
    databricks_host = os.getenv("DATABRICKS_HOST")
    databricks_token = os.getenv("DATABRICKS_TOKEN")

    url = f"{databricks_host}/api/2.0/pipelines/{pipeline_id}/events"

    headers = {
        "Authorization": f"Bearer {databricks_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return f"Error retrieving pipeline runs: {response.text}"

    data = response.json()

    runs = []

    # Extract the most recent pipeline events
    for event in data.get("events", [])[:5]:
        runs.append({
            "timestamp": event.get("timestamp"),
            "event_type": event.get("event_type"),
            "message": event.get("message")
        })

    # Create a nicely formated output
    summary = []
    for r in runs:
        summary.append(
            f"{r['timestamp']} | {r['event_type']} | {r['message']}"
        )

    return "\n".join(summary)


# ------------------------------------------------------------
# Register all tools the agent can use
# ------------------------------------------------------------

tools = [get_pipeline_runs]


# ------------------------------------------------------------
# Agent prompt
# ------------------------------------------------------------

# This is the instruction that guides the agent.
# It tells the model when tools should be used.

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a data platform assistant.

You have access to tools that can retrieve information from Databricks.

IMPORTANT:
If the user asks about pipeline runs, pipeline status, or pipeline history,
you MUST use the appropriate tool instead of answering from your own knowledge.

Never explain how to check pipelines manually.
Always call the tool when pipeline information is requested.
"""
    ),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])


# ------------------------------------------------------------
# Create the tool-calling agent
# ------------------------------------------------------------

# This agent allows the LLM to:
#
# 1. Read the user question
# 2. Decide if a tool is needed
# 3. Call the tool
# 4. Use the tool result to produce the final answer

agent = create_tool_calling_agent(
    _llm,
    tools,
    prompt
)


# ------------------------------------------------------------
# Agent executor
# ------------------------------------------------------------

# The executor actually runs the agent logic:
#
# LLM reasoning
# → tool execution
# → return final answer

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True   # shows reasoning steps in the terminal
)


# ------------------------------------------------------------
# Small transformation: add robot emoji
# ------------------------------------------------------------

def add_robot(text: str) -> str:
    """
    Simple transformation step to show how outputs
    can be modified before sending them back to Slack.
    """
    return f"🤖 {text}"


# ------------------------------------------------------------
# Main interface used by the Slack bot
# ------------------------------------------------------------

def ask_llm(question: str) -> str:
    """
    This function is called by the Slack bot.

    It sends the user question to the agent and
    returns the final response.
    """

    logger.info(f"User question: {question}")

    # Invoke the agent
    result = agent_executor.invoke({
        "input": question
    })

    # LangChain returns a dictionary
    # We extract the final agent response
    reply = result["output"]

    logger.info(f"Agent reply: {reply}")

    # Add the robot emoji before sending back to Slack
    reply = add_robot(reply)

    return reply