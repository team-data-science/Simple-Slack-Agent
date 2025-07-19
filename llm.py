import requests

def ask_llm(prompt: str) -> str:
    url = "http://host.docker.internal:11434/api/generate"
    payload = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("response", "⚠️ No response from model.")
    except Exception as e:
        print(f"❌ LLM error: {e}")
        return "Sorry, there was a problem generating a response."