# Używamy lekkiego obrazu Pythona 3.10
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# katalog roboczy
WORKDIR /app

# Kopiujemy plik z wymaganiami i instalujemy biblioteki
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy kod źródłowy
COPY src/ /app/src/

COPY best.pt /app/src/best.pt

# Zmienna środowiskowa
ENV PYTHONPATH=/app

# Domyślna komenda
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]