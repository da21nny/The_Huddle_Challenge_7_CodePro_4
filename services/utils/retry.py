import time # Para manejar pausas de tiempo
from functools import wraps # Para conservar metadatos de la función
import requests # Para manejar errores de red

# funcion decoradora que permite reintentar una funcion si falla
def retry(max_reintentos=3, retraso=2): # Configura reintentos y tiempo de espera
    def decorator(funcion): # Recibe la función a decorar
        @wraps(funcion) # Mantiene el nombre original de la función
        def wrapper(*args, **kwargs): # Envuelve la función con la lógica de reintento
            intentos_realizados = 0 # Contador de intentos
            
            while intentos_realizados < max_reintentos: # Ciclo hasta cumplir los reintentos
                try: # Intenta ejecutar el código
                    # Ejecuta la función original
                    return funcion(*args, **kwargs) # Devuelve el resultado si tiene éxito
                
                except requests.exceptions.RequestException as error_de_red: # Captura fallos de red
                    # Manejo de error de conexión
                    intentos_realizados += 1 # Suma un intento fallido
                    print(f"⚠️ Falla {intentos_realizados}/{max_reintentos}. Reintentando...") # Avisa el estado
                    
                    if intentos_realizados >= max_reintentos: # Si no quedan más intentos
                        print("❌ Abortando.") # Avisa el fin de intentos
                        raise error_de_red # Lanza el error final
                        
                    # Espera antes de volver a intentar
                    time.sleep(retraso) # Pausa la ejecución
                    
        return wrapper # Devuelve la función envuelta
    return decorator # Devuelve el decorador configurado