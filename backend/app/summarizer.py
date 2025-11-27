import requests
import json
import os

# Получаем API ключ из переменной окружения
API_KEY = os.getenv("API_KEY")

# Определяем типы суммаризации с промптами
SUMMARIZATION_TYPES = {
    "brief": {
        "name": "Кратко",
        "prompt": "Создай очень краткое резюме текста в 2-3 предложениях, передающее только главную идею. Пиши на том же языке, что и исходный текст."
    },
    "detailed": {
        "name": "Подробно",
        "prompt": "Создай подробное резюме текста одним большим абзацем (5-7 предложений), охватывающее все основные детали и ключевые моменты, но без глубоких углублений. Пиши на том же языке, что и исходный текст."
    },
    "structured": {
        "name": "Структурированно",
        "prompt": "Создай структурированное резюме текста, разбитое на несколько абзацев по главам или темам. Каждый абзац должен начинаться с ключевой темы и содержать 3-4 предложения. Пиши на том же языке, что и исходный текст."
    },
    "bullet_points": {
        "name": "Ключевые пункты",
        "prompt": "Создай резюме текста в виде маркированного списка из 5-8 ключевых пунктов. Каждый пункт должен быть кратким (1-2 предложения) и отражать важную информацию. Используй символ • для маркировки. Пиши на том же языке, что и исходный текст."
    },
    "executive": {
        "name": "Для руководителей",
        "prompt": "Создай исполнительную суммаризацию: краткое резюме для руководителей в 3-4 предложениях, фокусируясь на ключевых выводах, цифрах и практических последствиях. Пиши на том же языке, что и исходный текст."
    }
}

def summarize_text(text, summary_type="brief"):
    """
    Args:
        text (str): Текст для суммаризации
        summary_type (str): Тип суммаризации (brief, detailed, structured, bullet_points, executive)
        
    Returns:
        dict: {"summary": str} в случае успеха или {"error": str} в случае ошибки
    """
    
    if not API_KEY:
        return {"error": "API_KEY не найден в переменных окружения"}
    
    if not text or not text.strip():
        return {"error": "Текст не может быть пустым"}
    
    # Проверяем, существует ли такой тип суммаризации
    if summary_type not in SUMMARIZATION_TYPES:
        return {"error": f"Неизвестный тип суммаризации: {summary_type}"}
    
    # Получаем промпт для выбранного типа
    system_prompt = SUMMARIZATION_TYPES[summary_type]["prompt"]
    
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
                "model": "mistralai/devstral-small-2505",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"Суммаризируй следующий текст:\n\n{text}"
                    }
                ],
            })
        )
        
        if response.status_code == 200:
            result = response.json()
            summary = result['choices'][0]['message']['content']
            return {
                "summary": summary,
                "type": summary_type,
                "type_name": SUMMARIZATION_TYPES[summary_type]["name"]
            }
        else:
            return {"error": f"Ошибка API: {response.status_code} - {response.text}"}
            
    except Exception as e:
        return {"error": f"Произошла ошибка: {str(e)}"}

def get_available_types():
    """
    Returns:
        dict: Словарь с типами суммаризации и их описаниями
    """
    return {
        key: {
            "name": value["name"],
            "id": key
        }
        for key, value in SUMMARIZATION_TYPES.items()
    }
