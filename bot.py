import time
import logging
from slack_sdk.web import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from config import SLACK_BOT_TOKEN, SLACK_APP_TOKEN
from llm import ask_llm

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Slack clients
web_client = WebClient(token=SLACK_BOT_TOKEN)
socket_client = SocketModeClient(app_token=SLACK_APP_TOKEN, web_client=web_client)

# Filter out bot's own messages
auth = web_client.auth_test()
BOT_USER_ID = auth.get("user_id")
logger.info(f"Bot user ID: {BOT_USER_ID}")


def process(client: SocketModeClient, req: SocketModeRequest):
    if req.type != "events_api":
        return
    client.send_socket_mode_response({"envelope_id": req.envelope_id})

    event = req.payload.get("event", {})
    # Only handle human text messages
    if "text" not in event or event.get("bot_id") or event.get("user") == BOT_USER_ID:
        return

    user_input = event["text"]
    channel = event["channel"]
    thread_ts = event.get("thread_ts") or event["ts"]

    logger.info(f"Received from {event.get('user')}: {user_input}")
    reply = ask_llm(user_input)
    logger.info(f"Replying: {reply}")

    web_client.chat_postMessage(
        channel=channel,
        text=reply,
        thread_ts=thread_ts
    )


if __name__ == "__main__":
    socket_client.socket_mode_request_listeners.append(process)
    print("Starting Slack Agent...", flush=True)
    socket_client.connect()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...", flush=True)
