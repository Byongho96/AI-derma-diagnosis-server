FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --timeout=1200 -r requirements.txt && \
    pip uninstall opencv-python -y && \
    pip install opencv-python-headless

COPY . .

RUN chmod +x /app/entrypoint.sh
RUN sed -i 's/\r$//' /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]