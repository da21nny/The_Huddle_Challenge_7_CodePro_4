import requests
import os
from dotenv import load_dotenv

load_dotenv() # Carga las variables del archivo .env automáticamente

AUTH_URL = os.getenv("AUTH_URL", "http://127.0.0.1:5001")
STATION_URL = os.getenv("STATION_URL", "http://127.0.0.1:5002")
RESERVATION_URL = os.getenv("RESERVATION_URL", "http://127.0.0.1:5003")

def main():
    print("===========================================")
    print("❄️  SISTEMA DE RESERVAS - PENGUIN ACADEMY  ❄️")
    print("===========================================")
    print("Asegúrate de que los 3 servicios estén corriendo en docker.")
    
    token = None
    headers = {}
    
    while not token:
        print("\n--- MENÚ DE INICIO ---")
        print("1. Iniciar sesión")
        print("2. Registrar nuevo usuario")
        print("3. Salir")
        
        option = input("Elige una opción (1-3): ")
        
        if option == "3":
            print("Saliendo del sistema...")
            return
            
        elif option == "1":
            user = input("Usuario: ")
            pwd = input("Contraseña: ")
            try:
                response = requests.post(f"{AUTH_URL}/login", json={"username": user, "password": pwd})
                if response.status_code == 200:
                    token = response.json().get("token")
                    headers = {"Authorization": f"Bearer {token}"}
                    print(f"✅ Autenticación exitosa. Bienvenido '{user}'.\n")
                else:
                    try:
                        error_msg = response.json().get('message', 'Error desconocido')
                        print(f"❌ Error: {error_msg}")
                    except requests.exceptions.JSONDecodeError:
                        print(f"❌ Error del Servidor ({response.status_code}): El servicio devolvió una respuesta no válida.")
                        print("💡 Tip: Verifica que la base de datos esté lista y el servicio de autenticación no haya fallado.")
            except requests.exceptions.ConnectionError:
                print("❌ Error: No se pudo conectar al servicio de Autenticación.")
                return
                
        elif option == "2":
            user = input("Nuevo Usuario: ")
            pwd = input("Nueva Contraseña: ")
            try:
                response = requests.post(f"{AUTH_URL}/register", json={"username": user, "password": pwd})
                if response.status_code == 201:
                    print("✅", response.json().get("message"))
                    print("Ahora puedes iniciar sesión.")
                else:
                    try:
                        error_msg = response.json().get('message', 'Error desconocido')
                        print(f"❌ Error: {error_msg}")
                    except requests.exceptions.JSONDecodeError:
                        print(f"❌ Error del Servidor ({response.status_code}): No se pudo procesar el registro.")
            except requests.exceptions.ConnectionError:
                print("❌ Error: No se pudo conectar al servicio de Autenticación.")
                return
        else:
            print("⚠️ Opción inválida.")
    
    while True:
        print("\n--- MENÚ PRINCIPAL ---")
        print("1. Ver mesas de evaluación disponibles")
        print("2. Registrar una nueva reserva")
        print("3. Ver todas las reservas")
        print("4. Editar nombre de una mesa")
        print("5. Eliminar una reserva")
        print("6. Salir")
        
        option = input("Elige una opción (1-6): ")
        
        if option == "1":
            print("\nConsultando mesas (GET /stations)...")
            try:
                res = requests.get(f"{STATION_URL}/stations", headers=headers)
                if res.status_code == 200:
                    print("Mesas disponibles:")
                    for obj in res.json().get("data", []):
                        print(f" - ID: {obj['id']} | {obj['nombre']}")
                else:
                    data = res.json()
                    print(f"Error {data.get('status')}: {data.get('message')}")
            except Exception as e:
                print(f"Error de conexión: {e}")
                
        elif option == "2":
            print("\n-- Nueva Reserva --")
            fecha = input("Ingrese fecha (ej. 2026-03-10): ")
            hora = input("Ingrese hora (ej. 14:00): ")
            mesa_id = input("Ingrese el ID de la mesa (1, 2 o 3): ")
            
            try:
                mesa_id = int(mesa_id)
            except ValueError:
                print("⚠️  Error: El ID de la mesa debe ser un número.")
                continue
                
            print("\nEnviando reserva (POST /reservations)...")
            payload = {
                "fecha": fecha,
                "hora": hora,
                "mesa_id": mesa_id
            }
            try:
                res = requests.post(f"{RESERVATION_URL}/reservations", headers=headers, json=payload)
                data = res.json()
                if res.status_code in [200, 201]:
                    print("✅", data.get("message"))
                else:
                    print(f"❌ Error {data.get('status')}: {data.get('message')}")
            except Exception as e:
                print(f"Error de conexión: {e}")
                
        elif option == "3":
            print("\nConsultando reservas (GET /reservations)...")
            try:
                res = requests.get(f"{RESERVATION_URL}/reservations", headers=headers)
                if res.status_code == 200:
                    reservas = res.json().get("data", [])
                    if len(reservas) == 0:
                        print("No hay reservas registradas aún.")
                    else:
                        print("Reservas registradas:")
                        for idx, r in enumerate(reservas, 1):
                            print(f" {idx}. Fecha: {r['fecha']} | Hora: {r['hora']} | Mesa ID: {r['mesa_id']} (Usuario: {r['usuario']})")
                else:
                    data = res.json()
                    print(f"Error {data.get('status')}: {data.get('message')}")
            except Exception as e:
                print(f"Error de conexión: {e}")

        elif option == "4":
            print("\n-- Editar Nombre de Mesa --")
            mesa_id = input("Ingrese el ID de la mesa a editar: ")
            nuevo_nombre = input("Ingrese el nuevo nombre: ")
            
            try:
                mesa_id = int(mesa_id)
            except ValueError:
                print("⚠️  Error: El ID de la mesa debe ser un número.")
                continue
                
            print(f"\nEnviando actualización (PUT /stations/{mesa_id})...")
            payload = {"nombre": nuevo_nombre}
            try:
                res = requests.put(f"{STATION_URL}/stations/{mesa_id}", headers=headers, json=payload)
                data = res.json()
                if res.status_code == 200:
                    print("✅", data.get("message"))
                else:
                    print(f"❌ Error {data.get('status')}: {data.get('message')}")
            except Exception as e:
                print(f"Error de conexión: {e}")
                
        elif option == "5":
            print("\n-- Eliminar Reserva --")
            reserva_id = input("Ingrese el ID de la reserva a eliminar: ")
            
            try:
                reserva_id = int(reserva_id)
            except ValueError:
                print("⚠️  Error: El ID de la reserva debe ser un número.")
                continue
                
            print(f"\nEnviando eliminación (DELETE /reservations/{reserva_id})...")
            try:
                res = requests.delete(f"{RESERVATION_URL}/reservations/{reserva_id}", headers=headers)
                data = res.json()
                if res.status_code == 200:
                    print("✅", data.get("message"))
                else:
                    print(f"❌ Error {data.get('status')}: {data.get('message')}")
            except Exception as e:
                print(f"Error de conexión: {e}")
                
        elif option == "6":
            print("\nSaliendo del sistema...")
            break
        else:
            print("⚠️ Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
    main()
