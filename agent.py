import os
import json

class Agent:
    def __init__(self):
        # Cargamos las herramientas disponibles al iniciar el agente
        self.setup_tools()
        
        # 'messages' es la memoria central del agente. 
        # Arranca siempre con el "System Prompt", que define su identidad y reglas estrictas.
        self.messages = [
            {
                "role": "system", 
                "content": "Eres Toto, mi asistente de inteligencia artificial personal y técnico. TIENES ACCESO COMPLETO a mi sistema local a través de las herramientas (tools) que se te proporcionan. REGLA OBLIGATORIA: Si te pido interactuar con mis archivos (como listar, leer o crear), DEBES invocar obligatoriamente la herramienta correspondiente. NUNCA te disculpes ni digas que no tienes acceso al sistema."
            }
        ]

    def setup_tools(self):
        # Definición del esquema de herramientas en formato estándar de OpenAI.
        # Es importante respetar esta estructura JSON para que el modelo entienda qué puede hacer.
        self.tools = [
            {
                "type": "function",
                "function": {  
                    "name": "list_files_in_dir",
                    "description": "Listar los archivos en un directorio especificado.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Directorio a leer. Para el directorio actual, usa estrictamente el valor '.' (punto). NUNCA uses '/'."
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {  
                    "name": "read_file",
                    "description": "Leer el contenido de un archivo.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Ruta del archivo a leer."
                            }
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {  
                    "name": "edit_file",
                    "description": "Editar el contenido de un archivo reemplazando prev_text con new_text. Crea el archivo si no existe.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Ruta del archivo a editar."
                            },
                            "prev_text": {
                                "type": "string",
                                "description": "Texto a reemplazar (puede ser vacío para archivos nuevos)."
                            },
                            "new_text": {
                                "type": "string",
                                "description": "El nuevo texto que reemplazará a prev_text (o el texto para un archivo nuevo)."
                            }
                        },
                        "required": ["path", "new_text"]
                    }
                }
            }
        ]
        


    # ==========================================
    # LÓGICA NATIVA DE LAS HERRAMIENTAS
    # ==========================================
    
    def list_files_in_dir(self, directory="."):
        # PARCHE DE SEGURIDAD (Sandboxing): 
        # Evitamos que el modelo intente escanear directorios raíz por error.
        if directory in ["/", "\\", "C:\\", "c:\\"]:
            directory = "."
            
        print(f"⚙️ [SISTEMA] Leyendo el directorio: {directory}")
        try:
            files = os.listdir(directory)
            return {"files": files}
        except Exception as e:
            return {"error": str(e)}
            
    def read_file(self, path):
        print(f"⚙️ [SISTEMA] Leyendo el archivo: {path}")
        try:
            # Usamos utf-8 para evitar problemas de codificación con tildes y caracteres especiales
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                return {"content": content}
        except Exception as e:
            err = f"Error al leer el archivo: {e}"
            print(f"❌ {err}")
            return {"error": err}
    
    def edit_file(self, path, prev_text, new_text):
        print(f"⚙️ [SISTEMA] Procesando el archivo: {path}")
        try:
            existed = os.path.exists(path)
            
            # Si el archivo existe y nos pasan texto a reemplazar, procedemos a editarlo
            if existed and prev_text:
                read_result = self.read_file(path)
                if "error" in read_result:
                    return read_result
                
                content = read_result["content"]
                
                # Validación de seguridad para no corromper el archivo si el texto no coincide
                if prev_text not in content:
                    return {"error": f"Texto '{prev_text}' no encontrado en el archivo. No se realizaron cambios."}
                
                content = content.replace(prev_text, new_text)
            else:
                # Si no existe, creamos la estructura de carpetas necesaria y un archivo nuevo
                dir_name = os.path.dirname(path)
                if dir_name:
                    os.makedirs(dir_name, exist_ok=True)
                content = new_text
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            action = "editado" if existed and prev_text else "creado"
            return {"success": f"Archivo {action} '{path}' exitosamente."}
        
        except Exception as e:
            err = f"Error al crear/editar el archivo '{path}': {e}"
            print(f"❌ {err}")
            return {"error": err}



    # ==========================================
    # ORQUESTADOR DE RESPUESTAS (El motor lógico)
    # ==========================================
    def process_response(self, assistant_msg):
        """
        Analiza y procesa el objeto devuelto por el LLM.
        Retorna True si el agente requiere usar una herramienta.
        Retorna False si el agente ya generó una respuesta conversacional final.
        """
        
        # CASO A: El agente decidió invocar una herramienta
        if assistant_msg.tool_calls:
            # Obligatorio por protocolo OpenAI: guardar en memoria la petición original
            self.messages.append(assistant_msg)

            for tool_call in assistant_msg.tool_calls:
                fn_name = tool_call.function.name
                args_str = tool_call.function.arguments
                
                # --- PARCHE DEFENSIVO INTELIGENTE ---
                # Soluciona un bug común en modelos SLM donde omiten el nombre de la función
                # pero envían los parámetros correctamente. Deducimos la herramienta por su payload.
                if not fn_name:
                    try:
                        args_dict = json.loads(args_str)
                        if "new_text" in args_dict or "prev_text" in args_dict:
                            fn_name = "edit_file"
                        elif "path" in args_dict:
                            fn_name = "read_file"
                        else:
                            fn_name = "list_files_in_dir"
                    except:
                        fn_name = "list_files_in_dir"

                print(f"\n⚙️ [SISTEMA] Toto solicitó la herramienta: {fn_name}")
                
                # Extracción segura de los parámetros enviados por el modelo
                try:
                    args_dict = json.loads(args_str) if args_str else {}
                except json.JSONDecodeError:
                    args_dict = {}

                # Enrutador de ejecución: Llama a la función de Python correspondiente
                if fn_name == "list_files_in_dir":
                    directorio_a_leer = args_dict.get("directory", ".")
                    resultado_herramienta = self.list_files_in_dir(directorio_a_leer)
                    print(f"⚙️ [SISTEMA] Archivos capturados: {resultado_herramienta.get('files', resultado_herramienta.get('error'))}")
                    
                elif fn_name == "read_file":
                    path = args_dict.get("path", "")
                    resultado_herramienta = self.read_file(path)
                    print(f"⚙️ [SISTEMA] Lectura completada (enviada al contexto).")
                    
                elif fn_name == "edit_file":
                    path = args_dict.get("path", "")
                    prev_text = args_dict.get("prev_text", "")
                    new_text = args_dict.get("new_text", "")
                    resultado_herramienta = self.edit_file(path, prev_text, new_text)
                    print(f"⚙️ [SISTEMA] Resultado: {resultado_herramienta}")
                else:
                    resultado_herramienta = {"error": f"Herramienta desconocida: {fn_name}"}

                # Inyectamos el resultado bruto de la ejecución a la memoria del agente.
                # El rol 'tool' le indica al modelo que esta es la respuesta del sistema operativo.
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": fn_name,
                    "content": json.dumps(resultado_herramienta)
                })

            # Retornamos True para avisarle al bucle principal que debe volver a consultar a la API
            return True  

        # CASO B: El agente responde conversando normalmente (sin requerir herramientas)
        elif assistant_msg.content:
            texto_respuesta = assistant_msg.content
            
            # --- FILTRO ANTI-ALUCINACIÓN (JSON Fallback) ---
            # Si el modelo sufre de "Format Confusion" e intenta responder con JSON en vez de texto plano,
            # forzamos el parseo para mostrarle al usuario únicamente el mensaje limpio.
            if texto_respuesta.strip().startswith("{"):
                try:
                    datos = json.loads(texto_respuesta)
                    texto_respuesta = datos.get("content", datos.get("response", datos.get("respuesta", texto_respuesta)))
                except json.JSONDecodeError:
                    pass
            
            print(f"🤖 Toto: {texto_respuesta}\n")
            
            # Persistimos la respuesta final en el historial
            self.messages.append({"role": "assistant", "content": texto_respuesta})
            
            return False 

        return False