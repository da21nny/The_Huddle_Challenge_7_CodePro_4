FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY services/reservation_service/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY services/reservation_service ./services/reservation_service
COPY services/utils ./services/utils
EXPOSE 5003
CMD ["python", "-u", "services/reservation_service/reservation.py"]
