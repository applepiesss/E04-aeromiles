FROM python:3.11-slim

# Tambahkan user non-root demi keamanan
RUN useradd -m myuser

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install dependencies sistem
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Berikan izin ke user non-root
RUN chown -R myuser:myuser /app
USER myuser

# Jalankan aplikasi
CMD ["gunicorn", "aeromiles.wsgi:application", "--bind", "0.0.0.0:8000"]