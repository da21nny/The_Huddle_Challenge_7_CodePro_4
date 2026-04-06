import time # Para manejar pausas de tiempo
from functools import wraps # Para conservar metadatos de la función
import requests # Para manejar errores de red

# funcion decoradora que permite reintentar una funcion si falla
def retry(max_retries: int = 3, delay: int = 2): # Configura reintentos y tiempo de espera
    def decorator(func): # Recibe la función a decorar
        @wraps(func) # Mantiene el nombre original de la función
        def wrapper(*args, **kwargs): # Envuelve la función con la lógica de reintento
            attempts = 0 # Contador de intentos
            
            while attempts < max_retries: # Ciclo hasta cumplir los reintentos
                try: # Intenta ejecutar el código
                    # Ejecuta la función original
                    return func(*args, **kwargs) # Devuelve el resultado si tiene éxito
                
                except requests.exceptions.RequestException as network_error: # Captura fallos de red
                    # Manejo de error de conexión
                    attempts += 1 # Suma un intento fallido
                    
                    if attempts >= max_retries: # Si no quedan más intentos
                        print(f"❌ Fallo {attempts}/{max_retries}. Abortando.") # Avisa el fin de intentos
                        raise network_error # Lanza el error final
                        
                    print(f"⚠️ Falla {attempts}/{max_retries}. Reintentando en {delay}s...") # Avisa el estado
                    # Espera antes de volver a intentar
                    time.sleep(delay) # Pausa la ejecución
                    
        return wrapper # Devuelve la función envuelta
    return decorator # Devuelve el decorador configurado