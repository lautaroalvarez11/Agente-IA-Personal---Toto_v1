from openai import OpenAI

# Conectamos la librería estándar de OpenAI a mi Ollama local
client = OpenAI(
    base_url = 'http://localhost:11434/v1',
    api_key='ollama', # Se pone por protocolo, pero no valida nada
)

# Modelo elegido para el agente (puede modificarse):
selected_model = "llama3.2:1b"

# Contiene el historial de mensajes entre el usuario y el agente
messages = [
    {"role": "system", "content": "Eres un asistente personal útil que habla español, detallista, amable y con perfil técnico."}
]

while True:
    user_input = input("Ingrese un mensaje: ").strip()

    # Validamos si el usuario no escribió nada
    if not user_input:
        print("No se ingresó ningún mensaje. Por favor, intente de nuevo.")
        continue
    
    # Validamos si el usuario quiere salir del chat
    if user_input.lower() in ("salir", "exit", "bye"):
        print("Saliendo del chat. ¡Hasta luego!")
        break

    # Agregamos el mensaje del usuario al historial
    messages.append({"role": "user", "content": user_input})


    response = client.responses.create(
        model = (selected_model),
        input = messages
    )

    # Obtenemos la respuesta del agente y la agregamos al historial
    assistant_reply = response.output_text
    messages.append({"role": "assistant", "content": assistant_reply})

    print(f"Respuesta del agente: {assistant_reply}")

