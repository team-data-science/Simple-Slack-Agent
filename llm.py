import requests

# Send a prompt to a local Ollama model and return the generated text.
def ask_llm(prompt: str) -> str:
    
    # Ollama API running on the host machine (Docker-Desktop compatible)
    url = "http://host.docker.internal:11434/api/generate"
    
    # Request body for the LLM generation API
    payload = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    }

    try:
        # Make the HTTP POST request to the LLM
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        # Extract the model output (Ollama uses "response" field)
        return response.json().get("response", "⚠️ No response from model.")
    
    except Exception as e:
        # Catch network errors, timeouts, or invalid responses
        print(f"❌ LLM error: {e}")
        return "Sorry, there was a problem generating a response."