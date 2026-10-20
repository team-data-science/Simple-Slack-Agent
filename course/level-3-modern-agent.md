# Level 3: The Modern Agent with LangGraph

This is the version I'd build today. Same Slack bot, same Databricks tool, but the agent is one `create_agent()` call and the steps around it are a small LangGraph graph. After Level 2 you know what this hides from you, and that's the whole point.

```bash
git checkout level-3
```

## What changed since Level 2

Put the old agent and the new agent next to each other:

```bash
git diff level-2:agents/llm_reasoning.py level-3:agents/llm_langchain_agent.py
```

And the bot itself:

```bash
git diff level-2 level-3 -- bot.py requirements.txt
```

What you'll see:

- **`create_tool_calling_agent` + `AgentExecutor` + `ChatPromptTemplate` are gone.** It's one `create_agent(model, tools, system_prompt)` now. No `agent_scratchpad`, no executor. The tool calling loop you watched in Level 2 still happens, LangChain just runs it for you.
- **The tool handles errors.** `get_pipeline_runs` checks for missing credentials, uses a timeout, and returns an error message instead of crashing. The agent then explains the error in Slack instead of going silent.
- **The answer comes back as messages.** The agent returns `{"messages": [...]}` with everything that happened: your question, the tool call, the tool result, and the final answer. `[-1]` is always the final answer.
- **No more `BOT_MODE`.** `bot.py` imports `ask_llm` from `agents/llm_langgraph.py` directly. Simpler, and honestly that's what you want once you've picked your approach.
- **No more memory.** Every question is a fresh conversation again. Challenge 2 brings it back, the modern way.

## The two agent files

| File | What it shows |
|---|---|
| `agents/llm_langchain_agent.py` | The agent piped into a formatting step: `_agent \| RunnableLambda(...)`. Short and good enough for a lot of bots |
| `agents/llm_langgraph.py` (used by `bot.py`) | The same agent as a node in a LangGraph graph: `START → agent → format → END` |

Read `llm_langgraph.py` from top to bottom, it's written as a story. `ask_llm_simple()` is the agent without LangGraph, then the same thing comes as a graph with a shared state (`AgentState`), two nodes, and edges between them.

So why the graph if two nodes is basically a pipe? Because the next step is free. You want a validation step, a retry when the answer is empty, or routing to a different agent depending on the question? Add a node and an edge. The comments in the file show you exactly how. Everybody talks about "multi-agent systems" right now. For a Slack bot like this you don't need that, but the graph is the thing that lets you grow into it without rewriting your code.

## Run it

With Docker:

```bash
docker build -t slack-agent:level-3 .
docker run --rm --env-file .env slack-agent:level-3
```

Or directly on your machine, which is nice while you're changing code because you skip the rebuild:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
OLLAMA_API_URL=http://localhost:11434 python bot.py
```

(Outside Docker there's no `host.docker.internal`, so we point the bot at `localhost` for this run. The environment variable wins over the value in `.env`.)

Either way you should see:

```
Starting Slack Agent...
```

Now test the tool in Slack:

```
show me the runs for databricks pipeline: your-pipeline-id
```

The cool thing is, you can test this without Databricks. If you don't have the credentials set, the agent still calls the tool, the tool returns "Databricks credentials are missing", and the bot tells you exactly that in Slack. That's how you know the tool calling works.

> **Note:** Mistral is fine for this, but it's not the best at tool calling. If the agent sometimes answers from its own knowledge instead of calling the tool, try `ollama pull qwen2.5` and change `model="mistral"` in `agents/llm_langgraph.py` to `model="qwen2.5"`.

## Ask your AI assistant

- "In `agents/llm_langgraph.py`, what does `create_agent` do internally that I had to do myself with `AgentExecutor` before? Compare it with `agents/llm_reasoning.py` from the `level-2` tag."
- "Print out every message in `result["messages"]` for a question that triggers the tool. Explain what each message is."
- "How does a node in `StateGraph` update the state? What happens if `format_node` returns a key that isn't in `AgentState`?"
- "Show me how I would add a conditional edge that sends the flow back to the agent if the reply is empty."

## Challenge

Start your own branch: `git checkout -b my-level-3 level-3`.

1. **Add a Slack formatting node.** Models write markdown like `**bold**`, but Slack uses `*bold*`. Add a `slack_format` node between `agent` and `format` that fixes this.
   You're done when your graph has three nodes and bold text shows up correctly in Slack.
2. **Bring memory back, the modern way.** Instead of the hand-built history from Level 2, use a LangGraph checkpointer with the Slack thread as the conversation ID. Hint: look at `InMemorySaver` from `langgraph.checkpoint.memory`, the `checkpointer` parameter of `create_agent`, and `config={"configurable": {"thread_id": ...}}` when you invoke it. You need to pass `thread_ts` from `bot.py` into `ask_llm()` again.
   You're done when follow-up questions work inside a thread, and a new thread starts fresh.
3. **Stretch: retry on empty answers.** Add a conditional edge after `agent` that loops back once if the reply is empty.

## Next

You've got all the pieces. In [Level 4](level-4-your-own-tool.md) you make this bot useful for your own work.
