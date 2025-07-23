import time
import logging
from slack_sdk.web import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from config import SLACK_APP_TOKEN, SLACK_BOT_TOKEN
from llm import ask_llm

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Slack clients
web_client = WebClient(token=SLACK_BOT_TOKEN)
socket_client = SocketModeClient(app_token=SLACK_APP_TOKEN, web_client=web_client)

# Fetch and store the bot's user ID to filter out self-messages
auth_response = web_client.auth_test()
BOT_USER_ID = auth_response.get("user_id")
logger.info(f"🤖 Bot user ID is {BOT_USER_ID}")

def process(client: SocketModeClient, req: SocketModeRequest):
    if req.type != "events_api":
        return
    # Acknowledge the event to Slack
    client.send_socket_mode_response({"envelope_id": req.envelope_id})

    event = req.payload.get("event", {})
    # Ignore non-text events and messages from bots (including ourselves)
    if "text" not in event:
        return
    if event.get("bot_id") or event.get("user") == BOT_USER_ID:
        return

    user_input = event["text"]
    channel = event["channel"]
    thread_ts = event.get("thread_ts") or event["ts"]

    logger.info(f"💬 Received from {event.get('user')}: {user_input}")

    # Query the LLM for a reply
    reply = ask_llm(user_input)
    logger.info(f"🔁 Replying: {reply}")

    # Send the reply back into the same Slack thread
    web_client.chat_postMessage(
        channel=channel,
        text=reply,
        thread_ts=thread_ts
    )

if __name__ == "__main__":
    socket_client.socket_mode_request_listeners.append(process)
    print("🚀 Starting LangChain Slack Agent...", flush=True)
    socket_client.connect()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down", flush=True)