import time # Importa el modulo de tiempo
from functools import wraps # Importa el decorador para mantener metadatos
import requests # Importa la libreria para peticiones HTTP

class CircuitBreakerOpenException(Exception): # Define una excepcion personalizada para el circuito abierto
    pass # Clase vacia solo para heredar de Exception

def circuit_breaker(max_failures: int = 3, time_window: int = 10): # Define la funcion principal del circuit breaker
    """
    Patrón Circuit Breaker.
    Protege al sistema dejando de enviar peticiones temporalmente si el servicio destino está caído.
    """
    def decorator(func): # Define el decorador que recibe la funcion original
        failure_count = 0 # Variable para contar cuantas veces ha fallado
        last_failure_time = 0.0 # Variable para guardar cuando fue el ultimo fallo
        circuit_state = "CLOSED" # Variable para rastrear el estado actual del circuito
        
        @wraps(func) # Asegura que la funcion envuelta mantenga su nombre y docstring
        def wrapper(*args, **kwargs): # Define la funcion que envuelve la ejecucion real
            nonlocal failure_count, last_failure_time, circuit_state # Permite modificar variables del ambito superior
            
            if circuit_state == "OPEN": # Verifica si el circuito esta bloqueando peticiones
                elapsed_time = time.time() - last_failure_time # Calcula cuanto tiempo ha pasado desde el fallo
                
                if elapsed_time > time_window: # Revisa si ya paso el tiempo de espera necesario
                    circuit_state = "HALF_OPEN" # Cambia el estado para intentar una nueva peticion
                    print("🔄 Circuit Breaker: Probando conexión nuevamente...") # Informa que se hara una prueba
                else: # Si todavia no pasa el tiempo de espera
                    raise CircuitBreakerOpenException("🚨 Circuit Breaker ABIERTO: Petición bloqueada.") # Lanza error por circuito bloqueado

            try: # Intenta ejecutar la operacion protegida
                result = func(*args, **kwargs) # Ejecuta la funcion original y guarda el resultado
                
                if circuit_state == "HALF_OPEN": # Verifica si veniamos de un estado de prueba exitoso
                    print("✅ Circuit Breaker: Conexión recuperada. Circuito CERRADO.") # Informa que el servicio funciona de nuevo
                    circuit_state = "CLOSED" # Cambia el estado a normal o cerrado
                    failure_count = 0 # Reinicia el contador de errores acumulados
                    
                return result # Devuelve el resultado de la funcion ejecutada
            
            except requests.exceptions.RequestException as network_error: # Captura fallos especificos de red o peticiones
                failure_count += 1 # Incrementa el contador de fallos ocurridos
                last_failure_time = time.time() # Actualiza el momento exacto del ultimo error
                print(f"❌ Fallo {failure_count}/{max_failures} al conectar.") # Muestra el progreso de fallos permitidos
                
                if failure_count >= max_failures: # Revisa si se alcanzo el limite maximo de errores
                    circuit_state = "OPEN" # Abre el circuito para bloquear futuras llamadas
                    print(f"🛑 Circuit Breaker ABIERTO! Bloqueando peticiones por {time_window} segundos.") # Informa del bloqueo temporal
                    
                raise network_error # Lanza el error original para ser manejado externamente
                
        return wrapper # Devuelve la funcion envuelta procesada
    return decorator # Devuelve el decorador listo para usarse