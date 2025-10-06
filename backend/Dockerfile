FROM python:3.11-slim-bookworm AS build

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies including Tesseract OCR and its dependencies
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    gcc \
    libpq-dev

# Create cache directory for transformers with proper permissions
RUN mkdir -p /home/appuser/.cache/huggingface && \
    chown -R 1000:1000 /home/appuser/.cache

COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Debugging: List files in /app to verify entrypoint.sh is present
RUN ls -la /app

COPY ./entrypoint.sh /app/

RUN if [ ! -f /app/entrypoint.sh ]; then echo "Entrypoint script not found!"; exit 1; fi
RUN sed -i 's/\r$//g' /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
