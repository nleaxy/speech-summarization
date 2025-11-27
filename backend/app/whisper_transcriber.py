# app/whisper_transcriber.py

import whisper
import librosa
import numpy as np
from pathlib import Path
from .summarizer import summarize_text

# ======================================================================
# ВАЖНО: Загружаем модель ОДИН РАЗ, когда этот модуль импортируется.
# Модель весит много, и загружать ее на каждый запрос - самоубийство.
# ======================================================================
print("INFO: Загрузка ML-модели Whisper (может занять время)...")
model = whisper.load_model("base")
print("INFO: Модель Whisper успешно загружена.")


def _add_speaker_diarization(transcription):
    """Приватная функция для эмуляции распределения голосов."""
    speakers = ["SPEAKER_01", "SPEAKER_02"]
    current_speaker = speakers[0]
    
    for i, segment in enumerate(transcription.get("segments", [])):
        if i > 0 and i % 2 == 0:
            current_speaker = speakers[1] if current_speaker == speakers[0] else speakers[0]
        segment["speaker"] = current_speaker
    
    return transcription

# ======================================================================
# ЭТО НАША ГЛАВНАЯ ФУНКЦИЯ, КОТОРУЮ БУДЕТ ДЕРГАТЬ БЭКЕНД
# ======================================================================
def run_transcription(audio_filepath: str, summary_type: str):
    """
    Принимает путь к аудиофайлу и возвращает результат транскрибации в виде словаря.
    """
    try:
        print(f"INFO: Начинаю обработку файла: {audio_filepath}")
        
        # 1. Загрузка аудио
        audio_data, _ = librosa.load(audio_filepath, sr=16000)
        audio_data = audio_data.astype(np.float32)
        
        # 2. Транскрибация
        result = model.transcribe(audio_data)
        
        # 3. Добавление "говорящих" (диаризация)
        result_with_speakers = _add_speaker_diarization(result)

        # 4. Формируем красивый итоговый JSON для ответа API
        final_result = {
            "text": result_with_speakers.get("text", "").strip(),
            "language": result_with_speakers.get("language", ""),
            "segments": [
                {
                    "start": segment.get("start"),
                    "end": segment.get("end"),
                    "text": segment.get("text", "").strip(),
                    "speaker": segment.get("speaker")
                }
                for segment in result_with_speakers.get("segments", [])
            ]
        }

        # --- ЭТАП 2: СУММАРИЗАЦИЯ ---
        # Теперь, когда у нас есть текст, мы передаем его в суммаризатор.
        
        # Проверяем, что текст не пустой
        if final_result and final_result.get("text"):
            print(f"INFO: Текст получен, отправляю на суммаризацию (тип: {summary_type})...")
            
            # Вызываем функцию summarize_text из соседнего файла
            summary_data = summarize_text(final_result["text"], summary_type)
            
            # Добавляем результат суммаризации в наш итоговый JSON
            final_result["summary_data"] = summary_data
        else:
            # Если текста нет, добавляем сообщение об ошибке
            final_result["summary_data"] = {"error": "Текст для суммаризации не был получен."}
        
        print(f"INFO: Обработка файла {audio_filepath} завершена успешно.")
        return final_result
        
    except Exception as e:
        print(f"ERROR: Произошла ошибка при обработке файла: {e}")
        # В случае ошибки возвращаем None, чтобы бэкенд понял, что что-то пошло не так
        return None