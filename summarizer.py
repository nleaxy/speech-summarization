import requests
import json
import os

# Получаем API ключ из переменной окружения
API_KEY = os.getenv("API_KEY")

def summarize_text(text):
    if not API_KEY:
        return {"error": "API_KEY не найден в переменных окружения"}
    
    if not text or not text.strip():
        return {"error": "Текст не может быть пустым"}
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "Text Summarizer",
            },
            data=json.dumps({
                "model": "mistralai/devstral-small-2505:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "Ты — помощник для суммаризации текста. Создай краткое, информативное резюме предоставленного текста на том же языке, что и исходный текст."
                    },
                    {
                        "role": "user",
                        "content": f"Очень кратко суммаризируй следующий текст:\n\n{text}"
                    }
                ],
            })
        )
        
        if response.status_code == 200:
            result = response.json()
            summary = result['choices'][0]['message']['content']
            return {"summary": summary}
        else:
            return {"error": f"Ошибка API: {response.status_code} - {response.text}"}
            
    except Exception as e:
        return {"error": f"Произошла ошибка: {str(e)}"}