# 🧠 Project 1: Local Slack LLM Agent

This is a fully local Slack bot that:
- Listens to questions in Slack using the RTM API
- Sends them to a local Ollama model (e.g., Mistral)
- Replies directly in the same Slack thread

## 🧱 Stack
- Python
- Slack SDK (`slack_sdk`)
- Local LLM via Ollama
- No FastAPI, no LangChain, no cloud

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