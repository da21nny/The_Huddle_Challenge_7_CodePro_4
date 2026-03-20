import time
from functools import wraps
import requests

def retry(max_retries=3, delay=2):
    """
    Patrón Retry Básicp.
    Si la función (petición HTTP) falla, espera 'delay' segundos y vuelve a intentar
    hasta un máximo de 'max_retries' veces.
    """
    def decorador(funcion):
        @wraps(funcion)
        def envoltorio(*args, **kwargs):
            intentos_realizados = 0
            
            while intentos_realizados < max_retries:
                try:
                    # Intenta ejecutar la petición
                    return funcion(*args, **kwargs)
                
                except requests.exceptions.RequestException as error_de_red:
                    # Si falla por problemas de red/conexión
                    intentos_realizados += 1
                    print(f"⚠️ Falla de conexión {intentos_realizados}/{max_retries}. Reintentando en {delay} segundos...")
                    
                    if intentos_realizados >= max_retries:
                        print("❌ Máximo de reintentos alcanzado. Abortando petición.")
                        raise error_de_red
                        
                    # Espera el tiempo definido antes del siguiente intento
                    time.sleep(delay)
                    
        return envoltorio
    return decorador
