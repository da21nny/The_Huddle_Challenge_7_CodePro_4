# Plan de Implementación: Desafío Microservicios "El Mamut"

Para modernizar el antiguo servidor monolítico "EL MAMUT", hemos definido una arquitectura basada en **Python y FastAPI**.

## 🏗️ Estructura del Proyecto

```text
The_Huddle_Challenge_6_CodePro_4/
├── services/               # Directorio raíz para todos los microservicios
│   ├── auth-service/       # Microservicio de Autenticación (JWT)
│   │   ├── app/
│   │   │   ├── main.py     # Punto de entrada FastAPI
│   │   │   ├── api/        # Rutas/Endpoints
│   │   │   ├── core/       # Configuración y Seguridad
│   │   │   ├── models/     # Modelos de DB (SQLAlchemy/Tortoise)
│   │   │   └── schemas/    # Esquemas Pydantic
│   │   ├── requirements.txt
│   │   └── .env
│   │
│   ├── product-service/    # Microservicio de Productos
│   │   └── app/ ...
│   │
│   └── order-service/      # Microservicio de Pedidos
│       └── app/ ...
│
├── docs/                   # Documentación técnica
└── README.md
```

## 🚀 Tecnologías
*   **Python 3.10+ / FastAPI**
*   **Pydantic** para validación de datos.
*   **Uvicorn** como servidor ASGI.
*   **JWT** para seguridad entre servicios.
*   **DB Independientes** (SQLite/PostgreSQL) para cada servicio.

---
*Este documento fue generado para asegurar que el equipo pueda continuar el desarrollo en cualquier entorno.*
