from fastapi import FastAPI
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv() 
API_KEY = os.getenv("API_KEY") 

if not API_KEY:
    raise ValueError("API_KEY")

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello"}

@app.get("/ia/{pregunta_id}")
def responder_ia(pregunta_id: str):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "content-type": "application/json",
        "Authorization": f"Bearer {API_KEY}" 
    }

    data = {
        "messages": [
            {
                "role": "system",
                "content": "Contéstame como un profesional en programación, solo español."
            },
            {
                "role": "user",
                "content": pregunta_id
            }
        ],
        "model": "mixtral-8x7b-32768",
        "temperature": 1,
        "max_tokens": 1024,
        "top_p": 1,
        "stream": False,
        "stop": None
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  
        respuesta = response.json()
        return {"ia_pregunta": respuesta['choices'][0]['message']['content']}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}}