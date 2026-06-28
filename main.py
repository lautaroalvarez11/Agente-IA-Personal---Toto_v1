from openai import OpenAI

# Conectamos la librería estándar de OpenAI a mi Ollama local
client = OpenAI(
    base_url = 'http://localhost:11434/v1',
    api_key='ollama', # Se pone por protocolo, pero no valida nada
)

# Modelo elegido para el agente (puede modificarse):
selected_model = "llama3.2:1b"

response = client.responses.create(
    model = (selected_model),
    input = "Hola, ¿cómo estás?"
)

print(response.output_text)

