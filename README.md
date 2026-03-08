# 🐧 Penguin Academy: Sistema de Reserva de Estaciones

¡Los monolitos han caído! Este proyecto implementa una arquitectura de **microservicios** para gestionar la reserva de estaciones de evaluación en un calendario, reemplazando al antiguo sistema "El Mamut".

## 📋 Sobre el Proyecto

El sistema permite a los usuarios autenticarse, consultar las mesas de evaluación disponibles (actualmente 3) y realizar reservas para una fecha y hora específica. La lógica de negocio asegura que **no pueda haber más de una reserva en la misma fecha, hora y mesa**.

## 🏗️ Arquitectura del Sistema

El proyecto está dividido en 3 microservicios independientes que se comunican a través de APIs REST:

1.  **Auth Service (Puerto 5001):** Gestiona la autenticación de usuarios y la validación de tokens. Base de datos: `auth.db`.
2.  **Station Service (Puerto 5002):** Administra el catálogo de estaciones/mesas disponibles. Base de datos: `station.db`.
3.  **Reservation Service (Puerto 5003):** Controla el calendario de reservas y valida la exclusividad de horarios. Base de datos: `reservation.db`.

Cada servicio es autónomo, posee su propia base de datos SQLite y se encarga de su propia inicialización.

## 📁 Estructura de Carpetas

```text
The_Huddle_Challenge_6_CodePro_4/
├── services/
│   ├── auth_service/
│   │   ├── auth.py          # Lógica del API Flask
│   │   └── database.py      # Inicialización de SQLite
│   ├── station_service/
│   │   ├── station.py       # Lógica del API Flask
│   │   └── database.py      # Inicialización de SQLite
│   └── reservation_service/
│       ├── reservation.py   # Lógica del API Flask
│       └── database.py      # Inicialización de SQLite
├── main.py                  # Orquestador/Cliente interactivo
├── requirements.txt         # Dependencias del proyecto
└── README.md                # Documentación
```

## 🛠️ Requisitos para Ejecutar

Para correr este proyecto necesitas:
- **Python 3.x** instalado.
- Las librerías **Flask** y **Requests**.

Puedes instalarlas rápidamente con:
```bash
pip install -r requirements.txt
```

## 🚀 Pasos para Ejecución

El sistema requiere que los 3 servicios estén activos simultáneamente. Abre **4 terminales** de forma independiente:

1.  **Terminal 1 (Auth):** `python services/auth_service/auth.py`
2.  **Terminal 2 (Stations):** `python services/station_service/station.py`
3.  **Terminal 3 (Reservations):** `python services/reservation_service/reservation.py`
4.  **Terminal 4 (Main):** `python main.py`

Una vez encendidos, usa el **Menú Principal** en la Terminal 4 para interactuar con el sistema. El usuario por defecto es `admin` con contraseña `secreto123`.

## 🧠 Conceptos Básicos Aplicados

-   **Microservicios:** Dividir una aplicación grande en servicios pequeños que hacen una sola cosa bien.
-   **API REST:** Forma de comunicación estándar usando HTTP (GET para leer, POST para crear).
-   **SQLite:** Base de datos ligera que no requiere un servidor externo, ideal para servicios independientes.
-   **Tokens Bearer:** Un "ticket" de seguridad que el cliente envía en cada petición para demostrar que está logueado.
-   **Integridad de Datos:** Uso de `UNIQUE` en la base de datos para evitar que dos personas reserven lo mismo al mismo tiempo.

---
*Desarrollado para el desafío de Penguin Academy. ¡Salva el sistema, conviértete en leyenda!* 🐧💻
- Edgar Vega - Da21nny - 2026 - Software Development
