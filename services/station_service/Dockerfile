FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY services/station_service/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY services/station_service ./services/station_service
COPY services/utils ./services/utils
EXPOSE 5002
CMD ["python", "-u", "services/station_service/station.py"]
