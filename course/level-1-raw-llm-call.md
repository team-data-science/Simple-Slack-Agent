# Level 1: The Raw LLM Call

This is the smallest possible Slack AI bot. No LangChain, no agent, nothing. A WebSocket listener for Slack and one HTTP POST to Ollama. I start here on purpose, because once you've seen this, every framework later is just "more stuff around these two things".

```bash
git checkout level-1
```

## What's in the code

Only two files matter here:

| File | What it does |
|---|---|
| `bot.py` | Connects to Slack over Socket Mode, receives every message event, and posts the answer back into the thread |
| `llm.py` | One function, `ask_llm()`, that sends the text to Ollama's `/api/generate` endpoint and returns the response |

The flow is really simple. Slack pushes an event to `process()` in `bot.py`, the bot acknowledges it right away so Slack doesn't retry, filters out stuff it shouldn't answer, calls `ask_llm(text)`, and posts the result with `chat_postMessage` using the `thread_ts` so the answer lands in the thread. That's it. That's a Slack AI bot.

## Run it

```bash
docker build -t slack-agent:level-1 .
docker run --rm --env-file .env slack-agent:level-1
```

(On Linux add `--add-host=host.docker.internal:host-gateway`, see [Level 0](level-0-setup.md#troubleshooting).)

You should see this in the logs, plus a lot of debug output from the Slack SDK:

```
🚀 Starting Socket Mode client...
```

Now go to your Slack channel and type:

```
What is a data pipeline?
```

The bot answers in the thread after a few seconds.

> **Heads up:** in this level the bot only answers messages that end with a `?`. I added that as a simple filter so it doesn't react to everything in the channel. If you write "tell me about Kafka" without a question mark, nothing happens, and that's on purpose.

## Things to notice

- **The model and URL are hardcoded** in `llm.py`: `mistral` and `http://host.docker.internal:11434`. The `OLLAMA_API_URL` in your `.env` is ignored here. We fix that in Level 2.
- **The bot has no memory.** Ask "What is Kafka?" and then "Who created it?" and it has no idea what "it" is. Every message is a brand new conversation.
- **The bot-message filter is weak.** It only skips events with `subtype == "bot_message"`. The messages your bot posts come back in as events too, and they don't always carry that subtype. So if the model ends its answer with a question mark, the bot can end up answering itself. In Level 2 you'll see the fix: the bot asks Slack for its own user ID and ignores its own messages.

## Ask your AI assistant

Open the repo on the `level-1` tag and try these:

- "Walk me through what happens in `bot.py` from the moment a Slack message arrives until the reply is posted. Point to the exact lines."
- "Why does `process()` call `send_socket_mode_response` before doing anything else? What happens if I remove it?"
- "What does `thread_ts = event.get("thread_ts") or event["ts"]` do, and what changes if I always use `event["ts"]`?"
- "What does `"stream": False` in `llm.py` do, and what would I need to change to stream the answer?"

## Challenge

Pick at least one. Do them on a new branch so you can always go back: `git checkout -b my-level-1 level-1`.

1. **Make it configurable.** Move the Ollama URL and the model name into `config.py` and read them from `.env`.
   You're done when you can switch to another model (for example `ollama pull llama3.2`) by only changing `.env`, and the bot still answers.
2. **Give it a personality.** Add a short instruction in front of the user's question, for example "Answer in max 3 sentences."
   You're done when the answers in Slack get noticeably shorter.
3. **Only answer when mentioned.** Replace the question mark rule. The bot should only answer when someone writes `@LLM Agent Bot` in the message.
   You're done when normal messages are ignored and mentions get an answer. Hint: mentions show up in the text as `<@U0123ABC>`, and `web_client.auth_test()` gives you the bot's own user ID.

## Next

In [Level 2](level-2-the-old-way.md) the bot gets memory and its first tool.
