FROM python:3.12-slim
WORKDIR /app
COPY apps/answer-core/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Bake the local multilingual embedder so the first request does not download it.
RUN python -c "from fastembed import TextEmbedding; TextEmbedding('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"
COPY apps/answer-core/src ./src
COPY psb_*.py ./
COPY data/fixtures /data/fixtures
COPY data/organizer /data/organizer
ENV PYTHONPATH=/app:/app/src
ENV PSB_KB_PATH=/data/organizer/kb
ENV CORS_ORIGINS=http://localhost:3000
EXPOSE 8090
CMD ["uvicorn", "answer_core.server:app", "--host", "0.0.0.0", "--port", "8090"]
