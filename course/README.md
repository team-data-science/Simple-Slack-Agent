# Build a Local Slack AI Agent

In this course you build a Slack bot that answers questions in a thread, runs fully local on Ollama, and calls real tools like the Databricks API when it needs data. You build it in levels, from a plain HTTP call to a modern LangChain agent wrapped in LangGraph, so you actually understand what the frameworks do for you.

## What you'll build

A Slack bot that runs in Docker on your laptop. You ask it "show me the runs for databricks pipeline: 1234" in Slack, it decides on its own to call the Databricks API, and it answers in the thread with the latest pipeline events. No cloud LLM, no API bill, everything stays on your machine.

## How this course works

I'm not going to walk you through every line of code in a video. Honestly, you don't need that, and in 2026 you have an AI coding assistant that explains code better than a 40 minute screen recording anyway. So this course works differently:

- **Every level is a git tag.** You check out the tag and you have the exact code for that level, working.
- **Every level has a short doc.** What changed, why it changed, how to run it, and the gotchas I ran into.
- **Every level ends with a challenge.** That's where you actually learn. Each challenge has a clear "you're done when" check.
- **Every level has a few prompts for your AI assistant.** Open the repo in Claude Code, Cursor or whatever you use and let it explain the parts you're curious about.
- **A few short videos** for the things that are easier to show than to write: the demo, the architecture, and what's really going on inside an agent.

The cool thing about doing it with tags is that you can diff the levels. `git diff level-2 level-3` shows you exactly what the modern LangChain version replaced, and that teaches you more than me typing it out in front of you.

## The levels

| Level | Git tag | What you learn | Time |
|---|---|---|---|
| [0. Setup](level-0-setup.md) | none | Slack app, tokens, Ollama, Docker | 30 min |
| [1. The raw LLM call](level-1-raw-llm-call.md) | `level-1` | A Slack bot is just a WebSocket listener plus one HTTP call to a model | 30 min |
| [2. The old way: memory and a reasoning agent](level-2-the-old-way.md) | `level-2` | What memory and tool calling actually are, the explicit way | 1 to 2 h |
| [3. The modern agent with LangGraph](level-3-modern-agent.md) | `level-3` | `create_agent` and LangGraph, and what they hide from you | 1 h |
| [4. Build your own tool](level-4-your-own-tool.md) | none, this one is yours | Make the agent useful for your own work | 1 to 3 h |

Levels 1 and 2 use the older LangChain style on purpose. I like them a lot because they show you what's going on behind the scenes. If you only care about the modern version, read the Level 2 doc quickly and jump to Level 3. But if you want to really understand agents, don't skip it.

## Get the code

```bash
git clone https://github.com/team-data-science/Simple-Slack-Agent.git
cd Simple-Slack-Agent
git fetch --tags
```

Then jump between levels like this:

```bash
git checkout level-1
```

> **Heads up:** these course docs live on the `modern-langchain-agent` branch. When you check out `level-1` the `course/` folder disappears, because that code is older than the docs. So keep the docs open on GitHub (or in a second editor window) while you work.

When you're done with a level and want to go back to the latest version:

```bash
git checkout modern-langchain-agent
```

## How to learn with your AI assistant

Every level has a section called "Ask your AI assistant". Copy those prompts into Claude Code, Cursor, Copilot chat or whatever you use, with the repo open. A few rules I'd stick to:

1. **Ask it to explain, not to fix.** You want to understand the code first. Changing it comes in the challenges.
2. **Make it point to lines.** "Show me the exact lines where..." keeps it honest and stops it from making stuff up.
3. **Run the code before you believe it.** If the assistant says the bot does X, send a message in Slack and check the logs.

## Show what you built

When your bot answers in Slack, take a screenshot and post it in the course community inside the Academy. Especially Level 4. I want to see which tools you connected.
