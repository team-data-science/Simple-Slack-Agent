# 🧠 Project 1: Local Slack LLM Agent

This is a fully local Slack bot that:
- Listens to questions in Slack using the WebSocket API (Socket Mode)
- Sends them to a local Ollama model (e.g., Mistral)
- Replies directly in the same Slack thread

## 🧱 Stack
- Python
- Slack SDK (`slack_sdk`)
- Local LLM via Ollama
- No FastAPI, no LangChain, no cloud

---

## 🪪 How to Get a Slack Bot Token (`xoxb-...`)

### ✅ Step 1: Create a Slack App

1. Go to: https://api.slack.com/apps
2. Click **"Create New App"**
3. Choose **"From scratch"**
4. Name it (e.g. `LLM Agent Bot`) and select your workspace

### 🔑 Step 2: Add Bot Token Scopes

1. In the left sidebar, go to **"OAuth & Permissions"**
2. Scroll down to **Bot Token Scopes**
3. Add the following scopes:
   - `app_mentions:read` *(optional)*
   - `channels:history`
   - `chat:write`
   - `im:history`
   - `im:write`
   - `mpim:history`
   - `groups:history` *(if you use private channels)*
   - `users:read` *(optional, if you want usernames)*

### 🤖 Step 3: Install the App to Your Workspace

1. In the sidebar, go to **"Install App"**
2. Click **"Install to Workspace"**
3. Approve the permissions
4. You will now see a **Bot User OAuth Token** like this:
   ```
   xoxb-1234...your-token-here
   ```
5. Copy this and add it to your `.env` file:
   ```env
   SLACK_BOT_TOKEN=xoxb-1234-your-token-here
   ```

### 💬 Step 4 (Optional): Add the Bot to a Channel

1. In Slack, go to a public channel
2. Type: `/invite @your-bot-name`
3. Your bot can now read and respond to messages in that channel

---

## 🚀 Setup

### 1. Clone the repo

```bash
git clone https://github.com/yourname/project-1-local-slack-agent
cd project-1-local-slack-agent
```

### 2. Create `.env` file

```env
SLACK_BOT_TOKEN=xoxb-your-bot-token
```

### 3. Start Ollama locally

```bash
ollama run mistral
```

Make sure it's running at `http://localhost:11434`.

### 4. Choose your LLM mode

By default, [bot.py](bot.py) uses the simple LLM (no reasoning). If you want to use the **reasoning agent** instead, open `bot.py` and swap the import:

```python
# Default (simple):
from llm_simple import ask_llm

# For reasoning agent, comment out the line above and uncomment this:
#from llm_reasoning import ask_llm
```

> **Note:** Both modes default to `mistral` so you only need to download one model. This works fine for the reasoning agent too, but if you want better tool-calling performance, consider switching to a **Qwen** model (e.g. `qwen2.5` or `qwen3`):
> ```bash
> ollama pull qwen2.5
> ```
> Then update the `model=` parameter in `llm_reasoning.py` accordingly.

---

## 🐳 Run with Docker

```bash
docker build -t slack-llm-bot .
docker run --env-file .env --network=host slack-llm-bot
```

> 🧠 `--network=host` is required so the container can access Ollama running on localhost.

---

## ✅ Done!

Now just send a question in your Slack channel, and your bot will respond right in the thread.

## Quick git reminder
git add .
git commit -m "first working version."
git push origin main