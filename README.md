# AI Speech Summarizer

Это Full-Stack веб-приложение для транскрибации и суммаризации аудиофайлов. Бэкенд написан на Python (Flask), фронтенд - на React (Vite).

## Стек технологий

*   **Бэкенд:** Python, Flask, OpenAI Whisper
*   **Фронтенд:** React, TypeScript, Vite, Tailwind CSS
*   **Суммаризация:** Внешнее API (OpenRouter.ai)

---

## Инструкция по запуску проекта

### 1. Клонирование репозитория

```bash
git clone https://github.com/nleaxy/speech-summarization.git
cd speech_summary
```

### 2. Настройка Бэкенда

1.  **Создайте и активируйте виртуальное окружение:**
    ```bash
    # Создаем venv
    python -m venv venv
    
    # Активируем (Windows)
    .\venv\Scripts\activate
    
    # Активируем (macOS/Linux)
    source venv/bin/activate
    ```

2.  **Установите зависимости Python:**
    ```bash
    # (venv) должен быть активен
    pip install -r backend/app/requirements.txt
    ```

3.  **Создайте файл с API-ключом:**
    *   В папке `backend/` создайте файл `.env`.
    *   Добавьте в него ваш API-ключ от OpenRouter: `API_KEY="sk-or-v1-..."`

### 3. Настройка Фронтенда

1.  **Установите зависимости Node.js:**
    ```bash
    cd speech-ui
    npm install
    ```

2.  **Соберите фронтенд для продакшена:**
    ```bash
    npm run build
    ```

3.  **Скопируйте результат сборки в бэкенд:**
    *   Скопируйте файл `speech-ui/dist/index.html` в папку `backend/app/templates/`.
    *   Скопируйте всё содержимое папки `speech-ui/dist/assets/` в папку `backend/app/static/assets/` (создайте папку `assets` внутри `static`, если ее нет).

### 4. Запуск!

1.  **Вернитесь в корневую папку проекта.**
2.  **Запустите сервер Flask (убедитесь, что venv активен):**
    ```bash
    # (venv) должен быть активен
    python backend/run.py
    ```

3.  **Откройте приложение в браузере** по адресу: `http://localhost:5000`
