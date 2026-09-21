FROM python:3.12-slim

WORKDIR /News_Intelligence

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:/app/src

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY config ./config
COPY tests ./tests

CMD ["python", "-m", "news_intelligence.main"]