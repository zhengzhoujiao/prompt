FROM python:3.11-slim

WORKDIR /app

COPY server.py index.html manage.html prompt_local.json ./
COPY downloads ./downloads

CMD ["python", "server.py"]
