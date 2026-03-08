import requests

AUTH_URL = "http://127.0.0.1:5001"
STATION_URL = "http://127.0.0.1:5002"
RESERVATION_URL = "http://127.0.0.1:5003"

def main():
    print("===========================================")
    print("❄️  SISTEMA DE RESERVAS - PENGUIN ACADEMY  ❄️")
    print("===========================================")
    print("Asegúrate de que los 3 servicios Flask estén corriendo.")
    print("Iniciando sesión con usuario por defecto (admin)...")
    
    try:
        response = requests.post(f"{AUTH_URL}/login", json={"username": "admin", "password": "secreto123"})
        if response.status_code != 200:
            print("Error de autenticación. Credenciales inválidas.")
            return
            
        token = response.json().get("token")
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Autenticación exitosa como 'admin'.\n")
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servicio de Autenticación.")
        print("Por favor, ejecuta arrancar_servicios.bat o enciende los servicios manualmente.")
        return
    
    while True:
        print("\n--- MENÚ PRINCIPAL ---")
        print("1. Ver mesas de evaluación disponibles")
        print("2. Registrar una nueva reserva")
        print("3. Ver todas las reservas")
        print("4. Salir")
        
        opcion = input("Elige una opción (1-4): ")
        
        if opcion == "1":
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
                
        elif opcion == "2":
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
                if res.status_code == 201:
                    print("✅", data.get("message"))
                else:
                    print(f"❌ Error {data.get('status')}: {data.get('message')}")
            except Exception as e:
                print(f"Error de conexión: {e}")
                
        elif opcion == "3":
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
                
        elif opcion == "4":
            print("\nSaliendo del sistema...")
            break
        else:
            print("⚠️ Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
    main()
