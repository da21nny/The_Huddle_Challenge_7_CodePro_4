FROM python:3.12-slim
WORKDIR /app
# Variables para mejorar el comportamiento de Python en Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Instalamos dependencias
COPY services/auth_service/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# Copiamos el código del servicio y las utils compartidas
COPY services/auth_service ./services/auth_service
COPY services/utils ./services/utils
# Exponemos el puerto (por defecto 5001)
EXPOSE 5001
# Comando para iniciar el servicio
CMD ["python", "-u", "services/auth_service/auth.py"]
