FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY swarm ./swarm
COPY config ./config
RUN mkdir -p /app/data /app/outbox
CMD ["python","-m","swarm","daemon"]
