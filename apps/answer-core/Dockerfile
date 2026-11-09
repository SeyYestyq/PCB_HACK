FROM python:3.12-slim
WORKDIR /app
COPY apps/answer-core/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY apps/answer-core/src ./src
COPY data/fixtures /data/fixtures
ENV PYTHONPATH=/app/src
ENV PSB_KB_PATH=/data/fixtures/kb.jsonl
ENV CORS_ORIGINS=http://localhost:3000
EXPOSE 8090
CMD ["uvicorn", "answer_core.server:app", "--host", "0.0.0.0", "--port", "8090"]
