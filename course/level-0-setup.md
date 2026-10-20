# Level 0: Setup

This is the boring part, but it's the part where most people get stuck, so go through it slowly. At the end you have a Slack app with two tokens, Ollama running with the Mistral model, and Docker ready to go.

## Prerequisites

- A Slack workspace where you're allowed to install apps (a free personal workspace is perfect)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) on Mac or Windows, or Docker Engine on Linux
- [Ollama](https://ollama.com/download)
- Git
- Optional for the tool calling levels: a Databricks workspace and a personal access token. You can do the whole course without it, I'll show you how in Level 3.

## Step 1: Create the Slack app

1. Go to https://api.slack.com/apps
2. Click **Create New App**, then **From scratch**
3. Name it something like `LLM Agent Bot` and pick your workspace

## Step 2: Turn on Socket Mode and get the app token

Socket Mode is why this whole thing runs on your laptop. Slack pushes the messages to your bot over a WebSocket, so you don't need a public URL, no ngrok, nothing.

1. In the left sidebar go to **Socket Mode** and switch it on
2. Slack asks you to create an app-level token. Give it a name like `socket` and add the `connections:write` scope
3. Copy the token. It starts with `xapp-`. That's your `SLACK_APP_TOKEN`

## Step 3: Subscribe to message events

This is the step I always forget. Without it the bot connects fine and then just never receives anything.

1. Go to **Event Subscriptions** and switch it on
2. Under **Subscribe to bot events** add:
   - `message.channels` (public channels)
   - `message.im` (direct messages)
   - `message.groups` (only if you want it in private channels)
3. Click **Save Changes**

## Step 4: Add the bot token scopes

1. Go to **OAuth & Permissions**
2. Under **Bot Token Scopes** add:
   - `channels:history`
   - `chat:write`
   - `im:history`
   - `im:write`
   - `groups:history` (only for private channels)

## Step 5: Install the app and get the bot token

1. Go to **Install App** and click **Install to Workspace**
2. Approve the permissions
3. Copy the **Bot User OAuth Token**. It starts with `xoxb-`. That's your `SLACK_BOT_TOKEN`

> **Note:** every time you change scopes or events later, Slack asks you to reinstall the app. Do it, otherwise your changes don't apply.

## Step 6: Invite the bot to a channel

In Slack, open the channel you want to use and type:

```
/invite @LLM Agent Bot
```

Use whatever name you gave your app in Step 1.

## Step 7: Start Ollama with Mistral

Install Ollama, then pull the model:

```bash
ollama pull mistral
```

Check that the Ollama API is up:

```bash
curl http://localhost:11434/api/tags
```

You should see some JSON with `mistral` in the list of models. On Mac the Ollama app keeps the server running in the background. On Linux, if the curl fails, start it with `ollama serve`.

## Step 8: Create your .env file

In the root of the repo create a file called `.env`:

```env
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
OLLAMA_API_URL=http://host.docker.internal:11434

# Optional, only for the Databricks tool in Level 2 and 3
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi-your-token
```

Replace the values with your own tokens. Leave out the Databricks lines if you don't have a workspace.

> **Watch out:** no quotes around the values. Docker's `--env-file` passes quotes through literally, so `"xoxb-..."` becomes a broken token.

This is super important: do NOT commit this file. It's already in `.gitignore`, so just don't force-add it.

## Step 9: Check Docker

```bash
docker run --rm hello-world
```

If you see "Hello from Docker!" you're good. That's it for the setup.

## Troubleshooting

**The bot starts, but never reacts to messages**
Nine times out of ten this is Step 3. Check that the message events are subscribed, reinstall the app, and make sure you invited the bot into the channel you're typing in.

**`not_authed` or `invalid_auth` on startup**
You mixed up the tokens. `SLACK_BOT_TOKEN` is the `xoxb-` one, `SLACK_APP_TOKEN` is the `xapp-` one.

**The bot can't reach Ollama from inside Docker (`Connection refused`)**
Inside the container, `localhost` is the container itself, not your laptop. That's why we use `host.docker.internal`. On Docker Desktop (Mac and Windows) that works out of the box. On Linux add this flag to every `docker run` in this course:

```bash
--add-host=host.docker.internal:host-gateway
```

## Next

Go to [Level 1](level-1-raw-llm-call.md) and get your first answer in Slack.
