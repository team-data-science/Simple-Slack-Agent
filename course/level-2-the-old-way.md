# Level 2: The Old Way, Memory and a Reasoning Agent

This level is the one I like most, because nothing is hidden yet. You see how memory is really just old messages pasted back into the prompt, and you see an agent decide to call a tool, step by step, in your terminal. The LangChain style here is older (LangChain 0.2), and that's exactly why it's useful: the moving parts are still visible.

```bash
git checkout level-2
```

## What changed since Level 1

See it for yourself first:

```bash
git diff level-1 level-2 -- bot.py config.py
```

The big changes:

- **`bot.py` doesn't care which brain it uses anymore.** It reads `BOT_MODE` from the environment and imports the matching `ask_llm()`. Slack handling stays the same, only the LLM part swaps out.
- **The bot ignores its own messages properly.** It calls `web_client.auth_test()` once at startup, remembers its own user ID, and skips every event from that ID or with a `bot_id`.
- **No more question mark rule.** The bot answers every message in the channels it's in.
- **The Ollama URL comes from `config.py`** via `OLLAMA_API_URL`.

## The modes

| `BOT_MODE` | File | What it shows you |
|---|---|---|
| `llm_raw` | `workflows/llm_raw.py` | Old-school LangChain chain with `ConversationBufferWindowMemory`. It logs the full prompt, so you can see the memory |
| `llm_simple` (default) | `workflows/llm_simple.py` | Same idea, but explicit: a `deque` of the last 10 messages plus a system message, sent to `ChatOllama` |
| `llm_reasoning` | `agents/llm_reasoning.py` | Tool calling agent with `create_tool_calling_agent` and `AgentExecutor`, plus a Databricks tool |

> **Note:** `bot.py` also lists a `llm_reasoning_new_style` mode. Skip it here. It needs a newer LangChain than the `langchain==0.2.14` pinned on this tag, so it fails when you select it. That's what Level 3 is for.

## Run it

Build once:

```bash
docker build -t slack-agent:level-2 .
```

Then start it with the mode you want:

```bash
docker run --rm --env-file .env -e BOT_MODE=llm_raw slack-agent:level-2
```

You should see:

```
Starting Slack Agent with mode: llm_raw
```

Make sure `OLLAMA_API_URL=http://host.docker.internal:11434` is in your `.env`. The default in `config.py` on this tag has no `http://` in front, and depending on your LangChain version that breaks the connection to Ollama. I fixed that later, but on this tag just set it in `.env` and you're fine.

## Part 1: Memory is just text

Run `llm_raw`, then send these two messages in Slack:

```
What is Apache Kafka?
```

```
Who created it?
```

Now it knows what "it" is. Look at the logs, `llm_raw.py` prints the prompt it sends to the model:

```
Prompt sent to LLM: Human: What is Apache Kafka?
Assistant: 🤖 Apache Kafka is ...
Human: Who created it?
Assistant:
```

See? Nothing magic about it. "Memory" is the last few turns of the conversation pasted in front of your new question. The model itself remembers nothing.

Then run `llm_simple` and do the same. It's the same idea, but instead of one big text prompt it sends a list of messages (`SystemMessage`, `HumanMessage`, `AIMessage`) to a chat model. That's how every modern chat API works, and it's what we use from here on.

## Part 2: The agent decides to call a tool

Run the reasoning agent:

```bash
docker run --rm --env-file .env -e BOT_MODE=llm_reasoning slack-agent:level-2
```

And ask in Slack, with one of your own Databricks pipeline IDs:

```
show me the runs for databricks pipeline: your-pipeline-id
```

Because the executor runs with `verbose=True`, you see the agent think in the terminal: it gets your question, decides it needs `get_pipeline_runs`, calls it with the pipeline ID it pulled out of your text, gets the events back, and writes the final answer from them.

The thing is, the model never calls anything itself. It only answers with "I want to call `get_pipeline_runs` with `pipeline_id=...`". LangChain parses that, runs your Python function, and sends the result back to the model. The model decides, your code acts. Once that clicks, agents stop being mysterious.

Also look at how the model knows when to use the tool: it's the docstring of `get_pipeline_runs` plus the system prompt. Those are instructions for the model, not just comments for you.

> **Watch out:** if you don't have `DATABRICKS_HOST` and `DATABRICKS_TOKEN` set, the tool crashes on the request and the bot doesn't answer at all. That's one of the rough edges of this version. Challenge 2 below fixes it.

## Ask your AI assistant

- "In `workflows/llm_raw.py`, show me exactly where the memory gets loaded and where it gets saved. What would happen if I removed `save_context`?"
- "Compare `llm_raw.py` and `llm_simple.py`. What's the difference between `OllamaLLM` with a `PromptTemplate` and `ChatOllama` with a message list?"
- "In `agents/llm_reasoning.py`, what is `agent_scratchpad` in the prompt, and what goes into it during a run?"
- "Explain step by step what `AgentExecutor` does when the model wants to call `get_pipeline_runs`."

## Challenge

Start your own branch: `git checkout -b my-level-2 level-2`.

1. **Memory per thread.** Right now `_history` in `llm_simple.py` is one global list, so every user and every thread shares the same memory. Ask something in one thread and then something unrelated in another, and you'll see it mix them up. Change it so memory is kept per Slack thread.
   You're done when two parallel threads in Slack don't know about each other. Hint: `bot.py` already has the `thread_ts`, you need to pass it into `ask_llm()`.
2. **A fake tool for testing.** Add a `get_fake_pipeline_runs` tool to `llm_reasoning.py` that returns three hardcoded runs, one of them failed. Register it in `tools` and make the docstring clear enough that the agent picks it.
   You're done when you ask "did any of my test pipeline runs fail?" and the agent calls your tool and tells you which run failed. This is also how I'd test agents in general, by the way. Get the reasoning right with fake data first, then plug in the real API.

## Next

In [Level 3](level-3-modern-agent.md) you'll see how much of this the modern LangChain version does for you.
