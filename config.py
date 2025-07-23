import os
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "host.docker.internal:11434")