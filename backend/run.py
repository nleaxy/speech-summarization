# backend/run.py
from app.app import app
from dotenv import load_dotenv
import os

load_dotenv() # Эта команда читает .env файл

# Проверка, что ключ загрузился
if not os.getenv("API_KEY"):
    print("ВНИМАНИЕ: API_KEY не найден! Проверьте .env файл в папке backend.")
else:
    print("INFO: API_KEY успешно загружен.")

if __name__ == "__main__":
    app.run(debug=True, port=5000)