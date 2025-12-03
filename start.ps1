# start.ps1

# Устанавливаем заголовок окна для красоты
$Host.UI.RawUI.WindowTitle = "AI Speech Summarizer Installer"

# Очищаем экран
Clear-Host

# Выводим красивый заголовок
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " AI Speech Summarizer - Скрипт запуска" -ForegroundColor White
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Определяем путь к .env файлу
$envFile = "backend\.env"

# Проверяем, существует ли .env файл
if (-not (Test-Path $envFile)) {
    Write-Host "ВНИМАНИЕ: Файл с API-ключом не найден." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Для работы суммаризации требуется API-ключ от сервиса OpenRouter.ai"
    Write-Host "Пожалуйста, выполните следующие шаги:"
    Write-Host ""
    Write-Host "  1. Перейдите на сайт https://openrouter.ai/keys" -ForegroundColor Green
    Write-Host "  2. Создайте новый ключ (это бесплатно)."
    Write-Host "  3. Скопируйте ключ (он начинается с `sk-or-v1-...`)."
    Write-Host ""
    
    # Запрашиваем ключ у пользователя
    $apiKey = Read-Host "> Вставьте ваш API-ключ сюда и нажмите Enter"
    
    # Создаем .env файл и записываем в него ключ
    Set-Content -Path $envFile -Value "API_KEY=`"$apiKey`""
    
    Write-Host ""
    Write-Host "Отлично! Ключ сохранен в файл $envFile." -ForegroundColor Green
    Write-Host "Теперь можно запускать приложение."
    Write-Host ""
} else {
    Write-Host "INFO: .env файл найден. Пропускаем создание." -ForegroundColor Gray
}

# Запускаем Docker
Write-Host "Запускаем Docker. Первая сборка может занять 5-15 минут..." -ForegroundColor White
docker-compose up --build

Write-Host ""
Read-Host "Нажмите Enter для выхода..."