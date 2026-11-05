FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python data/seed.py

# Run as an unprivileged user; the SQLite directory must stay writable.
RUN useradd --system --uid 10001 --no-create-home appuser \
    && chown -R appuser /app/data
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
