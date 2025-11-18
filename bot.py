import logging
from slack_sdk.web import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from llm import ask_llm
from config import SLACK_APP_TOKEN, SLACK_BOT_TOKEN

# Enable verbose logging for debugging Slack events and LLM calls
logging.basicConfig(level=logging.DEBUG)

# Web API client used for posting messages back into Slack
web_client  = WebClient(token=SLACK_BOT_TOKEN)

# Socket Mode client opens a WebSocket connection to receive real-time events
socket_client = SocketModeClient(
    app_token=SLACK_APP_TOKEN,
    web_client=web_client
)

# Handle all incoming Socket Mode requests from Slack.
def process(client: SocketModeClient, req: SocketModeRequest):
    
    # Only handle standard message events
    if req.type != "events_api":
        return
    event = req.payload["event"]

    # Always ACK the event so Slack stops retrying it
    client.send_socket_mode_response({"envelope_id": req.envelope_id})

    # Ignore bot messages or events without text
    if event.get("subtype") == "bot_message" or "text" not in event:
        return

    text = event["text"]
    channel = event["channel"]
    
    # Respond in-thread. If no thread exists, Slack uses the main ts.
    thread_ts = event.get("thread_ts") or event["ts"]

    # Optional: Only respond to messages ending with a question mark
    if not text.strip().endswith("?"):
        return

    # Forward message to local LLM (Ollama)
    answer = ask_llm(text)

    # Send LLM response back into Slack
    web_client.chat_postMessage(
        channel=channel,
        text=answer,
        thread_ts=thread_ts
    )

if __name__ == "__main__":
    
    # Register the event processor callback
    socket_client.socket_mode_request_listeners.append(process)
    
    print("🚀 Starting Socket Mode client...", flush=True)
    
    # Open the WebSocket connection to Slack (non-blocking)
    socket_client.connect()   # non-blocking connect to Slack

    # Keep the process alive so events keep streaming
    try:
        # keep the main thread alive so events keep flowing
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Socket Mode client shutting down.", flush=True)

