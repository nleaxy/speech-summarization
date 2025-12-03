#!/bin/bash
echo ""
echo "================================================================"
echo " AI Speech Summarizer - Скрипт запуска (macOS/Linux)"
echo "================================================================"
echo ""

if [ ! -f "backend/.env" ]; then
    echo "ВНИМАНИЕ: Файл с API-ключом не найден."
    echo ""
    echo "Для работы суммаризации требуется API-ключ от сервиса OpenRouter.ai"
    echo "  1. Перейдите на сайт https://openrouter.ai/keys"
    echo "  2. Создайте и скопируйте новый ключ (начинается с \"sk-or-v1-...\")."
    echo ""
    
    read -p "> Вставьте ваш API-ключ сюда и нажмите Enter: " API_KEY
    
    echo "API_KEY=\"$API_KEY\"" > backend/.env
    
    echo ""
    echo "Отлично! Ключ сохранен в файл backend/.env."
    echo ""
fi

echo "Запускаем Docker. Первая сборка может занять 5-15 минут..."
docker-compose up --build