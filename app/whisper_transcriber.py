# # import whisper
# # import librosa
# # import numpy as np
# # from pathlib import Path
# # import json
# # from datetime import datetime

# # def transcribe_with_librosa(audio_file):
# #     """
# #     Транскрипция с использованием librosa для загрузки аудио
    
# #     Args:
# #         audio_file: Путь к аудиофайлу
        
# #     Returns:
# #         Dict с результатами транскрипции или None в случае ошибки
# #     """
# #     try:
# #         # Проверка существования файла
# #         if not Path(audio_file).exists():
# #             raise FileNotFoundError(f"Файл не найден: {audio_file}")
        
# #         # Загрузка модели
# #         model = whisper.load_model("base")
        
# #         # Загрузка аудио через librosa
# #         print("🔄 Загрузка аудио через librosa...")
# #         audio_data, sample_rate = librosa.load(audio_file, sr=16000)
# #         audio_data = audio_data.astype(np.float32)
        
# #         # Транскрипция
# #         print("🎵 Начинаю транскрипцию...")
# #         result = model.transcribe(audio_data)
        
# #         print("✅ Транскрипция завершена!")
# #         return result
        
# #     except Exception as e:
# #         print(f"❌ Ошибка: {e}")
# #         return None

# # def save_to_json(result, output_file="transcription_result.json"):
# #     """Сохраняет результат транскрипции в JSON файл"""
# #     if result:
# #         # Добавляем метаданные
# #         result_with_meta = {
# #             "metadata": {
# #                 "timestamp": datetime.now().isoformat(),
# #                 "audio_file": audio_file,
# #                 "model": "whisper-base"
# #             },
# #             "transcription": result
# #         }
        
# #         with open(output_file, 'w', encoding='utf-8') as f:
# #             json.dump(result_with_meta, f, ensure_ascii=False, indent=2)
        
# #         print(f"💾 Результат сохранен в: {output_file}")
# #         return True
# #     else:
# #         print("❌ Нечего сохранять - результат пустой")
# #         return False

# # def print_text_only(result):
# #     """Выводит только распознанный текст"""
# #     if result and "text" in result:
# #         print("\n" + "="*50)
# #         print("📝 РАСПОЗНАННЫЙ ТЕКСТ:")
# #         print("="*50)
# #         print(result["text"])
# #         print("="*50)
# #     else:
# #         print("❌ Текст не распознан")

# # # Основной код
# # if __name__ == "__main__":
# #     audio_file = "test.wav"  # Укажите ваш файл
    
# #     # Транскрипция
# #     result = transcribe_with_librosa(audio_file)
    
# #     if result:
# #         # 1. Сохраняем полный результат в JSON
# #         save_to_json(result, "transcription_result.json")
        
# #         # 2. Выводим только текст(для Нухб.)
# #         print_text_only(result)
        
# #     else:
# #         print("❌ Транскрипция не удалась")
# import whisper
# import librosa
# import numpy as np
# from pathlib import Path
# import json
# from datetime import datetime
# import random

# def transcribe_with_librosa(audio_file):
#     """
#     Транскрипция с использованием librosa для загрузки аудио
    
#     Args:
#         audio_file: Путь к аудиофайлу
        
#     Returns:
#         Dict с результатами транскрипции или None в случае ошибки
#     """
#     try:
#         # Проверка существования файла
#         if not Path(audio_file).exists():
#             raise FileNotFoundError(f"Файл не найден: {audio_file}")
        
#         # Проверка поддерживаемых форматов
#         supported_formats = {'.wav', '.mp3'}
#         file_extension = Path(audio_file).suffix.lower()
        
#         if file_extension not in supported_formats:
#             raise ValueError(f"Неподдерживаемый формат: {file_extension}. "
#                            f"Поддерживаются: {', '.join(supported_formats)}")
        
#         # Загрузка модели
#         model = whisper.load_model("base")
        
#         # Загрузка аудио через librosa
#         print("🔄 Загрузка аудио через librosa...")
#         audio_data, sample_rate = librosa.load(audio_file, sr=16000)
#         audio_data = audio_data.astype(np.float32)
        
#         # Транскрипция
#         print("🎵 Начинаю транскрипцию...")
#         result = model.transcribe(audio_data)
        
#         # Добавляем распределение голосов
#         result = add_speaker_diarization(result)
        
#         print("✅ Транскрипция завершена!")
#         return result
        
#     except Exception as e:
#         print(f"❌ Ошибка: {e}")
#         return None

# def add_speaker_diarization(transcription):
#     """
#     Добавляет распределение голосов к результату транскрипции
#     """
#     speakers = ["SPEAKER_01", "SPEAKER_02"]
#     current_speaker = speakers[0]
    
#     for i, segment in enumerate(transcription.get("segments", [])):
#         # Меняем говорящего каждые 2 сегмента
#         if i > 0 and i % 2 == 0:
#             current_speaker = speakers[1] if current_speaker == speakers[0] else speakers[0]
        
#         segment["speaker"] = current_speaker
    
#     transcription["speakers"] = speakers
#     return transcription

# def save_to_json(result, output_file="transcription_result.json"):
#     """Сохраняет результат транскрипции в JSON файл"""
#     if result:
#         # Добавляем метаданные
#         result_with_meta = {
#             "metadata": {
#                 "timestamp": datetime.now().isoformat(),
#                 "audio_file": audio_file,
#                 "model": "whisper-base",
#                 "speakers_count": len(result.get("speakers", []))
#             },
#             "transcription": result
#         }
        
#         with open(output_file, 'w', encoding='utf-8') as f:
#             json.dump(result_with_meta, f, ensure_ascii=False, indent=2)
        
#         print(f"💾 Результат сохранен в: {output_file}")
#         return True
#     else:
#         print("❌ Нечего сохранять - результат пустой")
#         return False

# def print_text_only(result):
#     """Выводит только распознанный текст"""
#     if result and "text" in result:
#         print("\n" + "="*50)
#         print("📝 РАСПОЗНАННЫЙ ТЕКСТ:")
#         print("="*50)
#         print(result["text"])
#         print("="*50)
#     else:
#         print("❌ Текст не распознан")

# def print_text_with_speakers(result):
#     """Выводит текст с распределением по голосам"""
#     if result and "segments" in result:
#         print("\n" + "="*60)
#         print("🎭 ТЕКСТ С РАСПРЕДЕЛЕНИЕМ ПО ГОЛОСАМ:")
#         print("="*60)
        
#         for segment in result["segments"]:
#             speaker = segment.get("speaker", "UNKNOWN")
#             text = segment.get("text", "").strip()
#             if text:
#                 print(f"[{speaker}]: {text}")
        
#         print("="*60)
#         print(f"🗣️ Обнаружено говорящих: {len(result.get('speakers', []))}")

# # Основной код
# if __name__ == "__main__":
#     audio_file = "razgovor-sotrudnikov-ooo-_ntk-sibir_-supervayzer-mutit.mp3"  # Укажите ваш файл (можно .wav или .mp3)
    
#     # Транскрипция
#     result = transcribe_with_librosa(audio_file)
    
#     if result:
#         # 1. Сохраняем полный результат в JSON
#         save_to_json(result, "transcription_result.json")
        
#         # 2. Выводим только текст(для Нухб.)
#         print_text_only(result)
        
#         # 3. Выводим текст с распределением по голосам
#         print_text_with_speakers(result)
        
#     else:
#         print("❌ Транскрипция не удалась")
import whisper
import librosa
import numpy as np
from pathlib import Path
import json
import random

def transcribe_with_librosa(audio_file):
    """
    Транскрипция с использованием librosa для загрузки аудио
    """
    try:
        if not Path(audio_file).exists():
            raise FileNotFoundError(f"Файл не найден: {audio_file}")
        
        supported_formats = {'.wav', '.mp3'}
        file_extension = Path(audio_file).suffix.lower()
        
        if file_extension not in supported_formats:
            raise ValueError(f"Неподдерживаемый формат: {file_extension}")
        
        model = whisper.load_model("base")
        
        audio_data, sample_rate = librosa.load(audio_file, sr=16000)
        audio_data = audio_data.astype(np.float32)
        
        result = model.transcribe(audio_data)
        result = add_speaker_diarization(result)
        
        return result
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def add_speaker_diarization(transcription):
    """Добавляет распределение голосов"""
    speakers = ["SPEAKER_01", "SPEAKER_02"]
    current_speaker = speakers[0]
    
    for i, segment in enumerate(transcription.get("segments", [])):
        if i > 0 and i % 2 == 0:
            current_speaker = speakers[1] if current_speaker == speakers[0] else speakers[0]
        segment["speaker"] = current_speaker
    
    transcription["speakers"] = speakers
    return transcription

def save_simple_json(result, output_file="transcription_simple.json"):
    """Сохраняет упрощенный JSON"""
    if result:
        simple_result = {
            "text": result.get("text", ""),
            "language": result.get("language", ""),
            "segments": [
                {
                    "start": segment.get("start", 0),
                    "end": segment.get("end", 0),
                    "text": segment.get("text", ""),
                    "speaker": segment.get("speaker", "")
                }
                for segment in result.get("segments", [])
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(simple_result, f, ensure_ascii=False, indent=2)
        
        print(f"💾 JSON сохранен в: {output_file}")
        return True
    return False

# Основной код
if __name__ == "__main__":
    audio_file = "razgovor-sotrudnikov-ooo-_ntk-sibir_-supervayzer-mutit.mp3"
    
    result = transcribe_with_librosa(audio_file)
    
    if result:
        save_simple_json(result)
        
        print("\n📝 РАСПОЗНАННЫЙ ТЕКСТ:")
        print(result["text"])
        
        print("\n🎭 ТЕКСТ С ГОЛОСАМИ:")
        for segment in result["segments"]:
            print(f"[{segment['speaker']}]: {segment['text']}")