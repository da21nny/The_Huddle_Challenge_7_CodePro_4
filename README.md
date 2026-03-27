# 🐧 Penguin Academy: Sistema de Reserva de Estaciones

¡Los monolitos han caído! Este proyecto implementa una arquitectura de **microservicios** para gestionar la reserva de estaciones de evaluación en un calendario, reemplazando al antiguo sistema "El Mamut".

## 📋 Sobre el Proyecto

El proyecto es una solución moderna, distribuida y resiliente para gestionar la reserva de estaciones de evaluación. Reemplazando un antiguo sistema monolítico, este sistema permite a los usuarios **autenticarse de forma segura mediante JWT (JSON Web Tokens)**, consultar estaciones disponibles (mesas de evaluación) y realizar reservas para fechas y horas específicas. 

La lógica de negocio principal asegura la exclusividad: **no puede haber reservas duplicadas en la misma fecha, hora y estación**. 

Destaca por estar construido con una arquitectura de microservicios, donde cada módulo posee su propia base de datos (PostgreSQL), cumple una única responsabilidad y se comunican ágilmente a través de APIs REST. Además, el código ha sido refactorizado recientemente aplicando Clean Code: traducciones de utilidades, nombres descriptivos en inglés y comentarios explicativos línea por línea. Está completamente dockerizado y listo para correr con `docker-compose`.

## 🏗️ Arquitectura del Sistema

El proyecto está dividido en 3 microservicios independientes que se comunican a través de APIs REST, respaldados por bases de datos PostgreSQL aisladas:

1.  **Auth Service (Puerto 5001):** Gestiona el login de usuarios, generando y emitiendo los tokens **JWT** para el manejo de sesiones seguras. Base de datos: `auth-db` (PostgreSQL).
2.  **Station Service (Puerto 5002):** Administra el catálogo de estaciones libres, validando el acceso a través de los tokens JWT emitidos de forma *stateless* (descentralizada). Base de datos: `station-db` (PostgreSQL).
3.  **Reservation Service (Puerto 5003):** Controla el calendario de reservas, validando la disponibilidad de horarios y controlando la exclusividad autorizando peticiones vía JWT. Base de datos: `reservation-db` (PostgreSQL).

Cuentan además con implementaciones robustas de patrones de resiliencia (**Circuit Breaker** y **Retry**), completamente comentadas para manejar interrupciones en la red y retardos de BBDD de forma elegante.

## 📁 Estructura de Carpetas

```text
The_Huddle_Challenge_7_CodePro_4/
├── docker-compose.yml       # Orquestación de contenedores y bases de datos
├── services/
│   ├── auth_service/
│   │   ├── auth.py          # Lógica del API Flask (Auth)
│   │   ├── database.py      # Inicialización y conexión a PostgreSQL
│   │   ├── Dockerfile       # Receta de la imagen Docker
│   │   └── requirements.txt
│   ├── station_service/
│   │   ├── station.py       # Lógica del API Flask (Stations)
│   │   ├── database.py      # Inicialización y conexión a PostgreSQL
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── reservation_service/
│   │   ├── reservation.py   # Lógica del API Flask (Reservations)
│   │   ├── database.py      # Inicialización y conexión a PostgreSQL
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── utils/
│       ├── circuit_breaker.py # Patrón Circuit Breaker
│       └── retry.py           # Patrón Retry
├── main.py                  # Cliente interactivo por consola
├── requirements.txt         # Dependencias del cliente (requests)
└── README.md                # Documentación
```

## 🛠️ Requisitos para Ejecutar

Para desplegar y usar este proyecto necesitas:
- **Docker** y **Docker Compose** instalados (para levantar la infraestructura).
- **Python 3.x** instalado (solo para ejecutar el cliente interactivo `main.py`).

Opcionalmente, para probar el cliente de forma aislada:
```bash
python -m venv .venv
# En Windows: .\.venv\Scripts\activate
# En Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
```

## 🚀 Pasos para Ejecución

El sistema se levanta de forma automatizada. Sigue estos pasos:

1.  **Levantar la Infraestructura:**
    Abre una terminal en la raíz del proyecto y ejecuta:
    ```bash
    docker-compose up --build -d
    ```
    *Nota: Las bases de datos y los microservicios se iniciarán. Los servicios tienen lógica de reintento para esperar a que las bases de datos estén listas.*

2.  **Ejecutar el Cliente Interactivo:**
    En tu terminal local (fuera de Docker), ejecuta:
    ```bash
    python main.py
    ```

3.  **Iniciar Sesión:**
    En el menú principal, usa las credenciales por defecto:
    - **Usuario:** `admin`
    - **Contraseña:** `secreto123`

## 🧠 Conceptos Básicos Aplicados

-   **Microservicios:** Dividir una aplicación grande en servicios pequeños y especializados.
-   **API REST:** Comunicación estándar usando HTTP (GET, POST, PUT, DELETE).
-   **Dockerización:** Empaquetado de cada servicio y base de datos (PostgreSQL) en contenedores aislados.
-   **Resiliencia Distribuida:** Implementación de patrones `Retry` y `Circuit Breaker` para manejar fallos de comunicación entre microservicios.
-   **Autenticación Descentralizada (JWT - Bearer):** Generación de JSON Web Tokens en el servicio central de Auth y validación *stateless* independiente en los demás microservicios.
-   **Clean Code y Refactorización:** Código fuente reestructurado (variables en español, funciones en inglés) con comentarios detallados línea por línea en utilidades transversales.

---
*Desarrollado para el desafío de Penguin Academy. ¡Salva el sistema, conviértete en leyenda!* 🐧💻
- Edgar Vega - Da21nny - 2026 - Software Development
