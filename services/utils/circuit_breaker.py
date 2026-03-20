import time
from functools import wraps
import requests

class CircuitBreakerOpenException(Exception):
    pass

def circuit_breaker(max_failures=3, time_window=10):
    """
    Patrón Circuit Breaker.
    Protege al sistema dejando de enviar peticiones temporalmente si el servicio destino está caído.
    """
    def decorador(funcion):
        cantidad_fallos = 0
        tiempo_ultimo_fallo = 0
        estado_circuito = "CERRADO"  # Estados: CERRADO (funciona), ABIERTO (roto), MEDIO_ABIERTO (probando)
        
        @wraps(funcion)
        def envoltorio(*args, **kwargs):
            nonlocal cantidad_fallos, tiempo_ultimo_fallo, estado_circuito
            
            # 1. Si está ABIERTO, revisamos si ya esperamos el tiempo suficiente
            if estado_circuito == "ABIERTO":
                tiempo_transcurrido = time.time() - tiempo_ultimo_fallo
                
                if tiempo_transcurrido > time_window:
                    estado_circuito = "MEDIO_ABIERTO"
                    print("🔄 Circuit Breaker: Probando conexión nuevamente...")
                else:
                    raise CircuitBreakerOpenException("🚨 Circuit Breaker ABIERTO: Petición bloqueada.")

            # 2. Intentamos ejecutar la petición
            try:
                resultado = funcion(*args, **kwargs)
                
                # Si todo sale bien y estábamos probando, cerramos el circuito (todo arreglado)
                if estado_circuito == "MEDIO_ABIERTO":
                    print("✅ Circuit Breaker: Conexión recuperada. Circuito CERRADO.")
                    estado_circuito = "CERRADO"
                    cantidad_fallos = 0
                    
                return resultado
            
            # 3. Si la petición falla (ej: el otro servicio está caído)
            except requests.exceptions.RequestException as error_de_red:
                cantidad_fallos += 1
                tiempo_ultimo_fallo = time.time()
                print(f"❌ Fallo {cantidad_fallos}/{max_failures} al conectar.")
                
                if cantidad_fallos >= max_failures:
                    estado_circuito = "ABIERTO"
                    print(f"🛑 Circuit Breaker ABIERTO! Bloqueando peticiones por {time_window} segundos.")
                    
                raise error_de_red
                
        return envoltorio
    return decorador
