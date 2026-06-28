# 🤖 Agente de IA Personal - Toto (Local & Sin Frameworks) / v1

¡Hola! Bienvenido al repositorio de la versión v1 de **Toto**, mi primer Agente de Inteligencia Artificial personal. 

Mi nombre es Lautaro Ezequiel Álvarez.
Como desarrollador adentrándome en el fascinante mundo de la IA, me propuse un desafío: **construir un agente autónomo desde cero, 100% local, y sin utilizar frameworks pesados** (como LangChain o CrewAI). El objetivo de este proyecto es entender a bajo nivel cómo funciona el razonamiento de un modelo, la inyección de memoria y la ejecución de herramientas (Tool Calling).

Este proyecto es la semilla de un ecosistema mucho más grande. La arquitectura fue diseñada con principios de Programación Orientada a Objetos (POO) para que las posibilidades de escalabilidad sean infinitas.

---

## 🚀 Características Principales

- **Memoria Contextual:** Mantiene el hilo de la conversación en tiempo real.
- **Uso de Herramientas (Tool Calling):** Capacidad para interactuar con el sistema operativo (listar, leer y crear/editar archivos).
- **100% Privado y Local:** Funciona sin internet utilizando [Ollama](https://ollama.com/) de fondo. Tus datos y archivos nunca salen de tu computadora.
- **Sandboxing y Seguridad:** Implementación de programación defensiva para evitar que la IA ejecute comandos destructivos o lea directorios sensibles.

---

## 🏗️ Decisiones de Arquitectura (El "Por Qué")

Al empezar este proyecto, tomé decisiones fundamentales para asegurar el aprendizaje y la robustez del código:

1. **Sin Frameworks:** Usar abstracciones mágicas oculta la verdadera lógica de los agentes. Quería construir el bucle de razonamiento y el enrutador de herramientas con mis propias manos en Python puro.
2. **La API de OpenAI como Puente:** Aunque el modelo corre localmente en Ollama, utilizo la librería oficial de `openai` en Python modificando el `base_url`. Esto significa que el código ya tiene un estándar de industria y el día de mañana puede conectarse a modelos gigantes en la nube cambiando solo una línea de código.
3. **El Modelo (Qwen vs. Llama):** Inicialmente probé con `llama3.2:1b`, pero los Modelos de Lenguaje Pequeños (SLMs) suelen sufrir de *"Format Confusion"* (se traban respondiendo en código JSON). Cambiar a `qwen3:1.7b` estabilizó drásticamente el uso de herramientas, ya que, aunque sigue siendo un modelo de menos de 2B, está mejor entrenado para separar texto natural de estructuras de datos.

---

## 🧠 Estructura del Código

El proyecto se divide en dos archivos principales para mantener una arquitectura limpia:

### 1. `main.py` (El Orquestador)
Es la puerta de entrada. Maneja la interfaz de usuario en la terminal y contiene el **Bucle de Eventos (Event Loop)**. Su trabajo es escuchar al usuario, enviar el contexto a la IA y decidir si debe seguir ejecutando herramientas o si ya puede mostrar la respuesta final.

### 2. `agent.py` (El Cerebro y las Manos)
Acá ocurre la magia. Es una clase de Python que encapsula:
- **El Prompt de Sistema:** La identidad de Toto y sus reglas estrictas.
- **El Catálogo de Herramientas:** Un esquema JSON estricto que le dice al modelo qué puede hacer.
- **Las Funciones Nativas:** Código Python real que lee y escribe en el disco.
- **El Procesador de Respuestas:** Un enrutador inteligente que intercepta las peticiones de la IA y ejecuta el código en el mundo real.

---

## 🛠️ Onboarding: Paso a Paso del Flujo de Trabajo

Si estás aprendiendo sobre agentes, así es como funciona Toto por debajo:

1. **La Petición:** El usuario escribe un comando (ej: *"Creá un archivo en mi directorio actual llamado notas.txt"*).
2. **El Razonamiento:** `main.py` envía esto a Ollama. El modelo detecta que necesita usar una herramienta para cumplir el objetivo.
3. **La Intercepción (Bug None):** Los modelos pequeños a veces cometen errores al generar el JSON (como olvidar el nombre de la herramienta). En `agent.py`, implementé un **parche defensivo** que deduce qué herramienta quería usar la IA leyendo sus argumentos.
4. **La Ejecución Segura:** Antes de tocar el disco, la función de Python valida que el agente no intente acceder a la raíz del sistema (`C:\`). A esto se le llama **Sandboxing**.
5. **La Retroalimentación:** El código ejecuta la acción, toma el resultado (ej: *"Archivo creado con éxito"*) y se lo re-inyecta al cerebro del modelo con el rol `"tool"`.
6. **La Respuesta Final:** Con la confirmación en su memoria, Toto genera una respuesta en texto natural para el usuario.

---

## ⚙️ Cómo ejecutarlo en tu máquina

### Requisitos previos
1. Instalar [Python 3.x](https://www.python.org/).
2. Instalar [Ollama](https://ollama.com/) y descargar el modelo ejecutando en la terminal: `ollama run qwen3:1.7b` (o tu modelo de preferencia).

### Instalación
1. Cloná este repositorio.
2. Abrí una terminal en la carpeta del proyecto y creá un entorno virtual:
   ```bash
   python -m venv env
   ```
3. Activá el entorno:
    - Windows:
    ```bash
    .\env\Scripts\Activate.ps1
    ```
    - Mac/Linux:
    ```bash
    source env/bin/Activate
    ```
4. Instalá la dependencia de conexión con el comando:
    ```bash
    pip install openai
    ```
5. ¡Encendé a Toto! con el comando:
    ```bash
    python .\main.py
    ```

---

## 🔮 Roadmap y Futuro del Proyecto

Las posibilidades de escalabilidad de este proyecto son inmensas. Mis próximos pasos para evolucionar a Toto son:

1. **Integración de Servidores MCP**: Conectar el esquema de herramientas actual con herramientas estándar de la industria para que pueda por ejemplo, leer repositorios de GitHub o ejecutar navegadores web automatizados.
2. **Memoria Vectorial (RAG)**: Incorporar una base de datos vectorial local para que Toto pueda leer miles de PDFs de documentación técnica y responder en base a ellos.
3. **Interfaz Gráfica**: Mejorarle el diseño UI de la terminal o en su defecto, migrar de la terminal de comandos a una interfaz web utilizando Streamlit o Gradio.
4. **Sistemas Multi-Agente**: Convertir a Toto en el "Agente Supervisor" que delegue tareas a sub-agentes especializados en código o investigación.

---

**Desarrollado con pasión, código y mucha prueba/error. ¡Cualquier feedback, issue o PR es bienvenido para seguir aprendiendo juntos!**

---

## 🧑‍💻​ Lautaro Ezequiel Álvarez
LinkedIn: (https://www.linkedin.com/in/lautaro-ezequiel-álvarez)