FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/services/task-service/src

WORKDIR /app

COPY services/task-service/requirements.txt /app/services/task-service/requirements.txt
RUN pip install --no-cache-dir -r /app/services/task-service/requirements.txt

COPY alembic.ini /app/alembic.ini
COPY main.py /app/main.py
COPY migrations /app/migrations
COPY services/task-service/src /app/services/task-service/src
COPY services/task-service/tests /app/services/task-service/tests
COPY services/task-service/docker/entrypoint.py /app/services/task-service/docker/entrypoint.py

EXPOSE 8000

ENTRYPOINT ["python", "services/task-service/docker/entrypoint.py"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
