import logging
from slack_sdk.web import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from llm import ask_llm
from config import SLACK_APP_TOKEN, SLACK_BOT_TOKEN

logging.basicConfig(level=logging.DEBUG)

web_client  = WebClient(token=SLACK_BOT_TOKEN)
socket_client = SocketModeClient(
    app_token=SLACK_APP_TOKEN,
    web_client=web_client
)

def process(client: SocketModeClient, req: SocketModeRequest):
    if req.type != "events_api":
        return
    event = req.payload["event"]
    # Acknowledge the event
    client.send_socket_mode_response({"envelope_id": req.envelope_id})

    # Only handle standard messages
    if event.get("subtype") == "bot_message" or "text" not in event:
        return

    text = event["text"]
    channel = event["channel"]
    thread_ts = event.get("thread_ts") or event["ts"]

    # (optional) basic question filter
    if not text.strip().endswith("?"):
        return

    answer = ask_llm(text)
    web_client.chat_postMessage(
        channel=channel,
        text=answer,
        thread_ts=thread_ts
    )

if __name__ == "__main__":
    socket_client.socket_mode_request_listeners.append(process)
    print("🚀 Starting Socket Mode client...", flush=True)
    socket_client.connect()   # non-blocking connect to Slack

    try:
        # keep the main thread alive so events keep flowing
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Socket Mode client shutting down.", flush=True)

