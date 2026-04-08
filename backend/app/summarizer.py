import requests
import json
import os

API_KEY = os.getenv("API_KEY")
MODEL_NAME = "nvidia/nemotron-3-super-120b-a12b:free"

SUMMARIZATION_TYPES = {
    "brief": {"name": "Кратко", "prompt": "Создай очень краткое резюме текста в 2-3 предложениях."},
    "detailed": {"name": "Подробно", "prompt": "Создай подробное резюме текста одним большим абзацем (5-7 предложений)."},
    "structured": {"name": "Структурированно", "prompt": "Создай структурированное резюме текста, разбитое на абзацы по темам."},
    "bullet_points": {"name": "Ключевые пункты", "prompt": "Создай резюме в виде маркированного списка из 5-8 пунктов."},
    "executive": {"name": "Для руководителей", "prompt": "Создай краткое резюме для руководителей, фокусируясь на выводах."}
}

# Темы (Domain Adaptation)
DOMAIN_PROMPTS = {
    "general": "Используй общеупотребительный язык, понятный любому человеку.",
    "informatics": (
        "Ты — эксперт в Computer Science. Используй строгую техническую терминологию. "
        "Обязательно делай упор на алгоритмы, архитектуру и стек технологий. "
        "Заменяй общие фразы профессиональными терминами (например, вместо 'программа' пиши 'ПО/приложение', "
        "вместо 'база' — 'СУБД')."
    )
}

def get_available_types():
    return {key: {"name": value["name"], "id": key} for key, value in SUMMARIZATION_TYPES.items()}

def summarize_text(text, summary_type="brief", topic="general"):
    if not API_KEY: return {"error": "API_KEY не настроен"}
    
    type_info = SUMMARIZATION_TYPES.get(summary_type, SUMMARIZATION_TYPES["brief"])
    type_instr = type_info["prompt"]
    domain_instr = DOMAIN_PROMPTS.get(topic, DOMAIN_PROMPTS["general"])
    
    system_prompt = f"{type_instr} {domain_instr} Пиши на том же языке, что и исходный текст."
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            data=json.dumps({
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Текст для суммаризации:\n\n{text}"}
                ]
            }),
            timeout=60
        )
        if response.status_code == 200:
            return {
                "summary": response.json()['choices'][0]['message']['content'],
                "type": summary_type,
                "type_name": type_info["name"],
                "topic": topic
            }
        return {"error": f"API Error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def compare_summary(text, summary_type="brief"):
    """
    НОВОЕ: Функция для сравнения 'До' и 'После'.
    Выполняет два запроса: обычный и с адаптацией под информатику.
    """
    res_before = summarize_text(text, summary_type, topic="general")
    res_after = summarize_text(text, summary_type, topic="informatics")
    
    return {
        "before": res_before.get("summary"),
        "after": res_after.get("summary")
    }

def ask_question_about_text(text, question):
    """Поисковая строка (Q&A)"""
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            data=json.dumps({
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": "Отвечай на вопросы строго по предоставленному тексту. Если ответа нет - так и скажи."},
                    {"role": "user", "content": f"Текст: {text}\n\nВопрос: {question}"}
                ]
            }),
            timeout=30
        )
        if response.status_code == 200:
            return {"answer": response.json()['choices'][0]['message']['content']}
        return {"error": "API Error"}
    except Exception as e:
        return {"error": str(e)}
