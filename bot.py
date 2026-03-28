import os
import time
import logging
from slack_sdk.web import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from config import SLACK_BOT_TOKEN, SLACK_APP_TOKEN

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# Select implementation at container startup
# ------------------------------------------------------------
# Pass BOT_MODE through docker up, for example:
#
# BOT_MODE=llm_raw
# BOT_MODE=llm_simple
# BOT_MODE=llm_reasoning
# BOT_MODE=llm_new_style
# ------------------------------------------------------------

BOT_MODE = os.getenv("BOT_MODE", "llm_simple").strip()


def get_ask_llm():
    if BOT_MODE == "llm_raw":
        from workflows.llm_raw import ask_llm
        return ask_llm

    if BOT_MODE == "llm_simple":
        from workflows.llm_simple import ask_llm
        return ask_llm

    if BOT_MODE == "llm_reasoning":
        from agents.llm_reasoning import ask_llm
        return ask_llm

    if BOT_MODE == "llm_reasoning_new_style":
        from agents.llm_reasoning_new_style import ask_llm
        return ask_llm

    valid = [
        "llm_raw",
        "llm_simple",
        "llm_reasoning",
        "llm_reasoning_new_style",
    ]
    raise ValueError(f"Invalid BOT_MODE='{BOT_MODE}'. Valid options are: {', '.join(valid)}")


ask_llm = get_ask_llm()
logger.info("Using BOT_MODE=%s", BOT_MODE)

# Initialize Slack clients
web_client = WebClient(token=SLACK_BOT_TOKEN)
socket_client = SocketModeClient(app_token=SLACK_APP_TOKEN, web_client=web_client)

# Filter out bot's own messages
auth = web_client.auth_test()
BOT_USER_ID = auth.get("user_id")
logger.info(f"Bot user ID: {BOT_USER_ID}")


def process(client: SocketModeClient, req: SocketModeRequest):
    
    # Only handle standard message events
    if req.type != "events_api":
        return
    
    # Always ACK the event so Slack stops retrying it
    client.send_socket_mode_response({"envelope_id": req.envelope_id})

    event = req.payload.get("event", {})
    
     # Ignore bot messages or events without text
    if "text" not in event or event.get("bot_id") or event.get("user") == BOT_USER_ID:
        return

    user_input = event["text"]
    channel = event["channel"]

    # Respond in-thread. If no thread exists, Slack uses the main ts.
    thread_ts = event.get("thread_ts") or event["ts"]
    logger.info(f"Received from {event.get('user')}: {user_input}")
    
    # Forward message to local LLM (Ollama)
    reply = ask_llm(user_input)
    logger.info(f"Replying: {reply}")

    # Send LLM response back into Slack
    web_client.chat_postMessage(
        channel=channel,
        text=reply,
        thread_ts=thread_ts
    )

if __name__ == "__main__":
    # Register the event processor callback
    socket_client.socket_mode_request_listeners.append(process)
    print(f"Starting Slack Agent with mode: {BOT_MODE}", flush=True)
    
    # Open the WebSocket connection to Slack (non-blocking)
    socket_client.connect()
    
    # Keep the process alive so events keep streaming
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...", flush=True)
