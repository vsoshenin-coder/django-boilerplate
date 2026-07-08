# Базовый образ с Python
FROM python:3.9-slim

# Отключаем буферизацию логов для Яндекс Облака
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt и ставим зависимости
COPY requirements.txt .

# ХАК ДЛЯ СТАРОГО ALLAUTH: обновляем pip и принудительно ставим совместимый setuptools
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "setuptools<60.0.0"

# ДОБАВИЛИ ФЛАГ --no-build-isolation
RUN pip install --no-cache-dir --no-build-isolation -r requirements.txt

# Копируем весь остальной код проекта
COPY . .

# Собираем статику. 
# Если вы используете S3 для статики, эту строку нужно удалить и запускать collectstatic вручную перед деплоем.
# Если статика отдается через WhiteNoise локально — оставляем.
RUN python manage.py collectstatic --noinput

# Яндекс Cloud сам назначит порт через переменную $PORT (обычно 8080)
# Обернули в sh -c, чтобы переменная $PORT гарантированно подставилась
CMD ["sh", "-c", "python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8080} --workers 2 --threads 2"]

