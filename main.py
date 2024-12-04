from fastapi import FastAPI
import requests
import json
from dotenv import load_dotenv
import os
from docx import Document  # Para manejar archivos .docx

load_dotenv() 
API_KEY = os.getenv("API_KEY") 

if not API_KEY:
    raise ValueError("API_KEY")

app = FastAPI()

# Función para leer contenido del archivo .docx
def leer_documento(docx_path: str) -> str:
    try:
        doc = Document(docx_path)
        contenido = ""
        for parrafo in doc.paragraphs:
            contenido += parrafo.text + "\n"
        return contenido.strip()
    except Exception as e:
        return f"Error al leer el documento: {e}"

# Ruta raíz
@app.get("/")
def read_root():
    return {"Hello": "World"}

# Ruta para manejar preguntas con contexto del documento
@app.get("/ia/{pregunta_id}")
def responder_ia(pregunta_id: str):
    # Leer contenido del documento instituciones.docx
    docx_path = "instituciones.docx"  # Asegúrate de que este archivo esté en el mismo directorio
    contexto = leer_documento(docx_path)

    if contexto.startswith("Error"):
        return {"error": contexto}  # Devuelve error si no se pudo leer el documento

    # Configuración de la solicitud a la API de IA
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "content-type": "application/json",
        "Authorization": f"Bearer {API_KEY}" 
    }

    data = {
        "messages": [
            {
                "role": "system",
                "content": f"Usa el siguiente contexto para responder: {contexto}"
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

    # Enviar solicitud a la API
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  
        respuesta = response.json()
        return {"ia_pregunta": respuesta['choices'][0]['message']['content']}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
