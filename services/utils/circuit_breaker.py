import time # Importa el modulo de tiempo
from functools import wraps # Importa el decorador para mantener metadatos
import requests # Importa la libreria para peticiones HTTP

class CircuitBreakerOpenException(Exception): # Define una excepcion personalizada para el circuito abierto
    pass # Clase vacia solo para heredar de Exception

def circuit_breaker(maximos_fallos=3, ventana_temporal=10): # Define la funcion principal del circuit breaker
    """
    Patrón Circuit Breaker.
    Protege al sistema dejando de enviar peticiones temporalmente si el servicio destino está caído.
    """
    def decorator(funcion): # Define el decorador que recibe la funcion original
        conteo_fallos = 0 # Variable para contar cuantas veces ha fallado
        instante_falla = 0 # Variable para guardar cuando fue el ultimo fallo
        estado_del_circuito = "CERRADO" # Variable para rastrear el estado actual del circuito
        
        @wraps(funcion) # Asegura que la funcion envuelta mantenga su nombre y docstring
        def wrapper(*args, **kwargs): # Define la funcion que envuelve la ejecucion real
            nonlocal conteo_fallos, instante_falla, estado_del_circuito # Permite modificar variables del ambito superior
            
            if estado_del_circuito == "ABIERTO": # Verifica si el circuito esta bloqueando peticiones
                segundos_transcurridos = time.time() - instante_falla # Calcula cuanto tiempo ha pasado desde el fallo
                
                if segundos_transcurridos > ventana_temporal: # Revisa si ya paso el tiempo de espera necesario
                    estado_del_circuito = "MEDIO_ABIERTO" # Cambia el estado para intentar una nueva peticion
                    print("🔄 Circuit Breaker: Probando conexión nuevamente...") # Informa que se hara una prueba
                else: # Si todavia no pasa el tiempo de espera
                    raise CircuitBreakerOpenException("🚨 Circuit Breaker ABIERTO: Petición bloqueada.") # Lanza error por circuito bloqueado

            try: # Intenta ejecutar la operacion protegida
                resultado_final = funcion(*args, **kwargs) # Ejecuta la funcion original y guarda el resultado
                
                if estado_del_circuito == "MEDIO_ABIERTO": # Verifica si veniamos de un estado de prueba exitoso
                    print("✅ Circuit Breaker: Conexión recuperada. Circuito CERRADO.") # Informa que el servicio funciona de nuevo
                    estado_del_circuito = "CERRADO" # Cambia el estado a normal o cerrado
                    conteo_fallos = 0 # Reinicia el contador de errores acumulados
                    
                return resultado_final # Devuelve el resultado de la funcion ejecutada
            
            except requests.exceptions.RequestException as error_detectado: # Captura fallos especificos de red o peticiones
                conteo_fallos += 1 # Incrementa el contador de fallos ocurridos
                instante_falla = time.time() # Actualiza el momento exacto del ultimo error
                print(f"❌ Fallo {conteo_fallos}/{maximos_fallos} al conectar.") # Muestra el progreso de fallos permitidos
                
                if conteo_fallos >= maximos_fallos: # Revisa si se alcanzo el limite maximo de errores
                    estado_del_circuito = "ABIERTO" # Abre el circuito para bloquear futuras llamadas
                    print(f"🛑 Circuit Breaker ABIERTO! Bloqueando peticiones por {ventana_temporal} segundos.") # Informa del bloqueo temporal
                    
                raise error_detectado # Lanza el error original para ser manejado externamente
                
        return wrapper # Devuelve la funcion envuelta procesada
    return decorator # Devuelve el decorador listo para usarse