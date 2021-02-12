FROM tiangolo/uvicorn-gunicorn-fastapi:latest
RUN pip install --upgrade pip && pip install requests
COPY . /app

