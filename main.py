import os
from dotenv import load_dotenv
from openai import OpenAI
from agent import Agent  # Importamos la clase Agent que contiene la memoria y las herramientas

# Cargamos las variables de entorno desde el archivo .env
load_dotenv()

# ==========================================
# 1. Configuración del Cliente
# ==========================================
# Usamos la librería oficial de OpenAI, pero al sistema
# le decimos que apunte a nuestro servidor local de Ollama.
client = OpenAI(
    base_url='http://localhost:11434/v1', # Puerto local por defecto de Ollama
    api_key=os.getenv("OPENAI_API_KEY", "ollama"), # Buscamos la clave en el entorno; si no existe, usamos "ollama" como fallback
) 

# Qwen es un modelo altamente optimizado para el uso de herramientas (Tool Calling)
selected_model = "qwen3:1.7b"

# Instanciamos nuestro agente Toto, que contiene la memoria y las herramientas
agent = Agent()

print("\n🤖 ¡Hola Soy Toto - v1! tu asistente personal, ya podemos conversar o ingresá 'salir'/'bye' para terminar la sesión.\n")



# ==========================================
# 2. Bucle Principal (Interacción con el usuario)
# ==========================================
while True:
    # Esperamos la entrada del usuario
    user_input = input("👤 Vos: ").strip()

    # Evitamos procesar mensajes vacíos
    if not user_input:
        continue
    
    # Condición de salida del programa
    if user_input.lower() in ("salir", "exit", "bye"):
        print("🤖 Toto: ¡Nos vemos!")
        break

    # Guardamos la petición del usuario en el historial centralizado del agente
    agent.messages.append({"role": "user", "content": user_input})



    # ==========================================
    # 3. Bucle Secundario (El "Cerebro" del Agente)
    # ==========================================
    # Este bucle sigue girando automáticamente si el agente decide que necesita 
    # usar herramientas antes de darle la respuesta final al usuario.
    while True:
        try:
            # Enviamos el historial completo y el catálogo de herramientas a Ollama
            response = client.chat.completions.create(
                model=selected_model,
                messages=agent.messages,
                tools=agent.tools
            )

            # Extraemos la respuesta bruta generada por el modelo
            assistant_msg = response.choices[0].message

            # Delegamos el procesamiento del mensaje a la clase Agent en agent.py.
            # Retorna True si ejecutó una herramienta, False si es texto final.
            called_tool = agent.process_response(assistant_msg)

            # Si el agente respondió con texto natural (no utilizó herramientas),
            # rompemos este sub-bucle y volvemos a escuchar al usuario.
            if not called_tool:
                break
                
        except Exception as e:
            # Capturamos errores (ej. si Ollama está apagado) para no tirar el programa
            print(f"\n❌ Error de conexión o ejecución: {e}\n")
            break