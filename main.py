from openai import OpenAI
import os
import json
from agent import Agent

# Conectamos la librería estándar de OpenAI a tu Ollama local
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama', # Se pone por protocolo, pero no valida nada
)

# Modelo elegido para el agente:
selected_model = "qwen3:1.7b"

# Instanciamos a Toto
agent = Agent()

print("\n🤖 Toto está en línea. Escribí 'salir' o 'bye' para terminar.\n")

# Bucle principal del chatbot
while True:
    user_input = input("👤 Vos: ").strip()

    # Validamos si el usuario no escribió nada
    if not user_input:
        print("No se ingresó ningún mensaje. Por favor, intente de nuevo.")
        continue
    
    # Validamos si el usuario quiere salir del chat
    if user_input.lower() in ("salir", "exit", "bye"):
        print("🤖 Toto: ¡Nos vemos!")
        break

    # Agregamos el mensaje del usuario al historial centralizado en el agente
    agent.messages.append({"role": "user", "content": user_input})

    # Bucle secundario: Se mantiene girando si Toto decide usar una herramienta
    while True:
        try:
            # Llamada a la API local usando el estándar de OpenAI
            response = client.chat.completions.create(
                model=selected_model,
                messages=agent.messages,
                tools=agent.tools
            )

            # Extraemos el objeto de mensaje devuelto por el modelo
            assistant_msg = response.choices[0].message

            # Le pasamos el mensaje a la clase Agent para que lo procese
            # Retorna True si ejecutó una herramienta, False si es texto final
            called_tool = agent.process_response(assistant_msg)

            # Si el agente no llamó a ninguna herramienta, rompemos este sub-bucle 
            # y volvemos a esperar el input del usuario
            if not called_tool:
                break
                
        except Exception as e:
            print(f"\n❌ Error de conexión o ejecución: {e}\n")
            break