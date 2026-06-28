import os
import json

class Agent:
    def __init__(self):
        self.setup_tools()
        # Contiene el historial de mensajes entre el usuario y el agente
        self.messages = [
            {
                "role": "system", 
                "content": "Eres Toto, mi asistente de inteligencia artificial personal y técnico. TIENES ACCESO COMPLETO a mi sistema local a través de las herramientas (tools) que se te proporcionan. REGLA OBLIGATORIA: Si te pido interactuar con mis archivos (como listar, leer o crear), DEBES invocar obligatoriamente la herramienta correspondiente. NUNCA te disculpes ni digas que no tienes acceso al sistema."
            }
        ]

    def setup_tools(self):
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
        
    # 1. Herramienta: Listar archivos
    def list_files_in_dir(self, directory="."):
        # PARCHE DE SEGURIDAD (Sandboxing): Evitamos que lea el disco entero
        if directory in ["/", "\\", "C:\\", "c:\\"]:
            directory = "."
            
        print(f"⚙️ [SISTEMA] Leyendo el directorio: {directory}")
        try:
            files = os.listdir(directory)
            return {"files": files}
        except Exception as e:
            return {"error": str(e)}
            
    # 2. Herramienta: Leer un archivo (Corregido el bug del video)
    def read_file(self, path):
        print(f"⚙️ [SISTEMA] Leyendo el archivo: {path}")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                return {"content": content} # El video omitió el return
        except Exception as e:
            err = f"Error al leer el archivo: {e}"
            print(f"❌ {err}")
            return {"error": err}
    
    # 3. Herramienta: Crear o Editar un archivo
    def edit_file(self, path, prev_text, new_text):
        print(f"⚙️ [SISTEMA] Procesando el archivo: {path}")
        try:
            existed = os.path.exists(path)
            if existed and prev_text:
                # Reutilizamos nuestra propia función de lectura
                read_result = self.read_file(path)
                if "error" in read_result:
                    return read_result
                
                content = read_result["content"]

                if prev_text not in content:
                    return {"error": f"Texto '{prev_text}' no encontrado en el archivo. No se realizaron cambios."}
                
                content = content.replace(prev_text, new_text)
            else:
                # Crear o sobreescribir completamente
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

    # Orquestador de respuestas
    def process_response(self, assistant_msg):
        """
        Retorna True si el agente ejecutó una herramienta (requiere otra iteración).
        Retorna False si el agente respondió con texto final.
        """
        # ==========================================
        # CASO A: El agente decidió usar una herramienta
        # ==========================================
        if assistant_msg.tool_calls:
            # Obligatorio por protocolo: guardar la intención
            self.messages.append(assistant_msg)

            for tool_call in assistant_msg.tool_calls:
                fn_name = tool_call.function.name
                args_str = tool_call.function.arguments
                
                # --- PARCHE DEFENSIVO (Bug 'None') Inteligente ---
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
                
                # Ejecución de la herramienta
                try:
                    args_dict = json.loads(args_str) if args_str else {}
                except json.JSONDecodeError:
                    args_dict = {}

                if fn_name == "list_files_in_dir":
                    directorio_a_leer = args_dict.get("directory", ".")
                    resultado_herramienta = self.list_files_in_dir(directorio_a_leer)
                    print(f"⚙️ [SISTEMA] Archivos capturados: {resultado_herramienta.get('files', resultado_herramienta.get('error'))}")
                    
                elif fn_name == "read_file":
                    path = args_dict.get("path", "")
                    resultado_herramienta = self.read_file(path)
                    print(f"⚙️ [SISTEMA] Lectura completada (enviada al cerebro de Toto).")
                    
                elif fn_name == "edit_file":
                    path = args_dict.get("path", "")
                    prev_text = args_dict.get("prev_text", "")
                    new_text = args_dict.get("new_text", "")
                    resultado_herramienta = self.edit_file(path, prev_text, new_text)
                    print(f"⚙️ [SISTEMA] Resultado: {resultado_herramienta}")
                else:
                    resultado_herramienta = {"error": f"Herramienta desconocida: {fn_name}"}

                # Inyectamos el resultado bruto a la memoria
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": fn_name,
                    "content": json.dumps(resultado_herramienta)
                })

            return True  # Ejecutó herramienta, avisamos a main.py que vuelva a iterar

        # ==========================================
        # CASO B: El agente responde conversando
        # ==========================================
        elif assistant_msg.content:
            texto_respuesta = assistant_msg.content
            
            # --- PARCHE ANTI-ALUCINACIÓN JSON ---
            if texto_respuesta.strip().startswith("{"):
                try:
                    datos = json.loads(texto_respuesta)
                    texto_respuesta = datos.get("content", datos.get("response", datos.get("respuesta", texto_respuesta)))
                except json.JSONDecodeError:
                    pass
            
            print(f"🤖 Toto: {texto_respuesta}\n")
            
            self.messages.append({"role": "assistant", "content": texto_respuesta})
            
            return False 

        return False