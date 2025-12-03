# =================================================================
# ЭТАП 1: Сборка Фронтенда (назовем этот этап 'frontend-builder')
# =================================================================
# Берем образ Node.js, чтобы получить npm и все инструменты
FROM node:20-alpine as frontend-builder

# Устанавливаем рабочую директорию
WORKDIR /frontend

# Копируем package.json и package-lock.json для установки зависимостей
# Мы копируем сначала только их, чтобы Docker кэшировал установку
COPY speech-ui/package*.json ./

# Принудительно чистим кэш npm и node_modules на всякий случай
RUN npm cache clean --force
RUN npm ci

# Копируем весь остальной код фронтенда
COPY speech-ui .

# Запускаем команду сборки
RUN npm run build


# =================================================================
# ЭТАП 2: Сборка Финального Бэкенд-Приложения
# =================================================================
# Начинаем заново с чистого образа Python
FROM python:3.9-slim

WORKDIR /app

# Устанавливаем FFMPEG и другие системные зависимости
RUN apt-get update && apt-get install -y ffmpeg build-essential && rm -rf /var/lib/apt/lists/*

# Копируем файл с зависимостями Python
COPY backend/app/requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бэкенда
COPY backend/app .

# Копируем РЕЗУЛЬТАТЫ СБОРКИ ФРОНТЕНДА из первого этапа ('frontend-builder')
# в папки нашего бэкенда.
COPY --from=frontend-builder /frontend/dist/index.html ./templates/
COPY --from=frontend-builder /frontend/dist/assets ./static/assets/

# Указываем порт
EXPOSE 5000

# Запускаем сервер Gunicorn, он надежнее, чем встроенный в Flask
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "300", "app:app"]