@echo off
CHCP 65001 > nul

echo.
echo ================================================================
echo  AI Speech Summarizer - Скрипт запуска
echo ================================================================
echo.

REM Проверяем наличие .env файла
IF NOT EXIST "backend\.env" (
    echo ВНИМАНИЕ: Файл с API-ключом не найден.
    echo.
    echo Для работы суммаризации требуется API-ключ от сервиса OpenRouter.ai
    echo Пожалуйста, выполните следующие шаги:
    echo.
    echo   1. Перейдите на сайт https://openrouter.ai/keys
    echo   2. Создайте новый ключ (это бесплатно).
    echo   3. Скопируйте ключ (он начинается с "sk-or-v1-...").
    echo.
    
    set /p API_KEY="> Вставьте ваш API-ключ сюда и нажмите Enter: "
    
    echo API_KEY="%API_KEY%" > backend\.env
    
    echo.
    echo Отлично! Ключ сохранен в файл backend\.env.
    echo Теперь можно запускать приложение.
    echo.
)

echo Запускаем Docker. Первая сборка может занять 5-15 минут...
docker-compose up --build

pause