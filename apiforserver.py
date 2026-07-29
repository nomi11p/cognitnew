import os
import requests
from dotenv import load_dotenv
from typing import Any

from manager import get_status

load_dotenv()
# ==========================================
# API KEYS
# ==========================================

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "google/gemini-2.5-flash"
)

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile"
)

MISTRAL_MODEL = os.getenv(
    "MISTRAL_MODEL",
    "mistral-small-latest"
)

COHERE_MODEL = os.getenv(
    "COHERE_MODEL",
    "command-r"
)

PROVIDER_STATUS = {
    "active_provider": None,
    "active_model": None,
    "providers": {
        "OpenRouter": {"healthy": False},
        "Groq": {"healthy": False},
        "Mistral": {"healthy": False},
        "Cohere": {"healthy": False},
    },
}

# ==========================================
# OPENROUTER CALLER
# ==========================================

def call_openrouter(prompt: str):

    if not OPENROUTER_API_KEY:
        return None

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

def call_groq(prompt: str):

    if not GROQ_API_KEY:
        return None

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": GROQ_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        },
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]


def call_mistral(prompt: str):

    if not MISTRAL_API_KEY:
        return None

    response = requests.post(
        "https://api.mistral.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MISTRAL_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        },
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]


def call_cohere(prompt: str):

    if not COHERE_API_KEY:
        return None

    response = requests.post(
        "https://api.cohere.com/v1/chat",
        headers={
            "Authorization": f"Bearer {COHERE_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": COHERE_MODEL,
            "message": prompt
        },
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data["text"]


def new_func(response):
    result = response.json()
    
# ==========================================
# MAIN PROVIDER
# ==========================================

def provider_generate_response(prompt: str, model_name: str | None = None):

    if not prompt:
        return "Prompt cannot be empty."


    providers = [
        (
            "OpenRouter",
            call_openrouter
        ),
        (
            "Groq",
            call_groq
        ),
        (
            "Mistral",
            call_mistral
        ),
        (
            "Cohere",
            call_cohere
        )
    ]


    for name, function in providers:

        try:

            response = function(prompt)

            if response:

                PROVIDER_STATUS["active_provider"] = name
                PROVIDER_STATUS["active_model"] = model_name
                PROVIDER_STATUS["providers"][name]["healthy"] = True

                return response


        except Exception as e:

            print(name, "FAILED:", e)

            PROVIDER_STATUS["providers"][name]["healthy"] = False



    raise Exception(
        "All AI providers are offline."
    )
