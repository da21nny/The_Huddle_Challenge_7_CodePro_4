# 🐧 Penguin Academy: Sistema de Reserva de Estaciones

¡Los monolitos han caído! Este proyecto implementa una arquitectura de **microservicios** para gestionar la reserva de estaciones de evaluación en un calendario, reemplazando al antiguo sistema "El Mamut".

## 📋 Sobre el Proyecto

El proyecto es una solución moderna, distribuida y resiliente para gestionar la reserva de estaciones de evaluación. Reemplazando un antiguo sistema monolítico, este sistema permite a los usuarios **autenticarse de forma segura mediante JWT (JSON Web Tokens)**, consultar estaciones disponibles (mesas de evaluación) y realizar reservas para fechas y horas específicas.

La lógica de negocio principal asegura la exclusividad: **no puede haber reservas duplicadas en la misma fecha, hora y estación**.

Destaca por estar construido con una arquitectura de microservicios, donde cada módulo posee su propia base de datos (PostgreSQL), cumple una única responsabilidad y se comunican ágilmente a través de APIs REST. Está completamente dockerizado, configurado mediante variables de entorno y listo para correr con `docker-compose`.

## 🏗️ Arquitectura del Sistema

El proyecto está dividido en 3 microservicios independientes que se comunican a través de APIs REST, respaldados por bases de datos PostgreSQL aisladas:

1. **Auth Service (Puerto 5001):** Gestiona el login de usuarios, generando y emitiendo los tokens **JWT** para el manejo de sesiones seguras. Base de datos: `auth-db` (PostgreSQL).
2. **Station Service (Puerto 5002):** Administra el catálogo de estaciones libres, validando el acceso de forma *stateless* mediante JWT. Base de datos: `station-db` (PostgreSQL).
3. **Reservation Service (Puerto 5003):** Controla el calendario de reservas, validando disponibilidad y autorizando peticiones vía JWT. Base de datos: `reservation-db` (PostgreSQL).

Cuentan además con implementaciones robustas de patrones de resiliencia (**Circuit Breaker** y **Retry**) para manejar interrupciones de red de forma elegante.

## 📁 Estructura de Carpetas

```text
The_Huddle_Challenge_7_CodePro_4/
├── docker-compose.yml       # Orquestación de contenedores y bases de datos
├── .env                     # Variables de entorno locales (NO se sube a Git)
├── .env.example             # Plantilla de variables de entorno
├── main.py                  # Cliente interactivo por consola
├── requirements.txt         # Dependencias del cliente
├── README.md                # Documentación
└── services/
    ├── auth_service/
    │   ├── auth.py          # Lógica del API Flask (Auth)
    │   ├── database.py      # Inicialización y conexión a PostgreSQL
    │   ├── Dockerfile       # Receta de la imagen Docker
    │   └── requirements.txt
    ├── station_service/
    │   ├── station.py       # Lógica del API Flask (Stations)
    │   ├── database.py      # Inicialización y conexión a PostgreSQL
    │   ├── Dockerfile
    │   └── requirements.txt
    ├── reservation_service/
    │   ├── reservation.py   # Lógica del API Flask (Reservations)
    │   ├── database.py      # Inicialización y conexión a PostgreSQL
    │   ├── Dockerfile
    │   └── requirements.txt
    └── utils/
        ├── circuit_breaker.py # Patrón Circuit Breaker
        └── retry.py           # Patrón Retry
```

## 🛠️ Requisitos Previos

- **Docker** y **Docker Compose** instalados (para levantar la infraestructura).
- **Python 3.x** instalado (para ejecutar el cliente interactivo `main.py`).

## 🚀 Pasos para Ejecución

### 1. Configurar las variables de entorno

El proyecto usa un archivo `.env` para evitar valores hardcodeados. Creá una copia del archivo de ejemplo:

**Windows (PowerShell):**
```powershell
copy .env.example .env
```

**Linux / Mac:**
```bash
cp .env.example .env
```

> Podés editar `.env` para ajustar puertos, contraseñas u otras configuraciones según tu entorno.

---

### 2. Crear el entorno virtual e instalar dependencias del cliente

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

**Linux / Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### 3. Levantar la infraestructura con Docker

Desde la raíz del proyecto (con Docker corriendo):
```bash
docker-compose up --build -d
```

> Las bases de datos y los microservicios se iniciarán automáticamente. Los servicios tienen lógica de reintento para esperar a que las bases de datos estén listas.

---

### 4. Ejecutar el cliente interactivo

Con el entorno virtual activado, ejecutá el cliente desde la raíz del proyecto:

**Windows:**
```powershell
py main.py
```

**Linux / Mac:**
```bash
python3 main.py
```

---

### 5. Registrarse e iniciar sesión

En el menú de inicio:
1. Elegí la opción **2** para registrar un nuevo usuario con tu nombre y contraseña.
2. Elegí la opción **1** para iniciar sesión con esas credenciales.

---

### 6. Detener los servicios

```bash
docker-compose down
```

## 🧠 Conceptos Aplicados

- **Microservicios:** Dividir una aplicación grande en servicios pequeños y especializados.
- **API REST:** Comunicación estándar usando HTTP (GET, POST, PUT, DELETE).
- **Dockerización:** Empaquetado de cada servicio y base de datos (PostgreSQL) en contenedores aislados.
- **Variables de Entorno (.env):** Configuración externalizada para evitar valores hardcodeados, compatible con Windows y Linux.
- **Resiliencia Distribuida:** Implementación de patrones `Retry` y `Circuit Breaker` para manejar fallos de comunicación entre microservicios.
- **Autenticación Descentralizada (JWT):** Generación de tokens en el Auth Service y validación *stateless* independiente en los demás microservicios.
- **Clean Code y Refactorización:** Código reestructurado con variables en español, funciones en inglés y comentarios detallados línea por línea.

---
*Desarrollado para el desafío de Penguin Academy. ¡Salva el sistema, conviértete en leyenda!* 🐧💻
- Edgar Vega - Da21nny - 2026 - Software Development
