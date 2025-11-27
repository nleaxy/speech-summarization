# app/app.py

import os
import uuid
from flask import Flask, jsonify, request
from flasgger import Swagger, swag_from
from werkzeug.utils import secure_filename

# =================================================================
# ВОТ ОНО! ИМПОРТИРУЕМ НАШ "ДВИЖОК" ИЗ СОСЕДНЕГО ФАЙЛА
# =================================================================
from .whisper_transcriber import run_transcription

# --- Настройка приложения ---
app = Flask(__name__)
# Указываем, что документация лежит в папке docs внутри нашего пакета
SWAGGER_TEMPLATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs/template.yml')

app.config['SWAGGER'] = {
    'title': 'Speech Recognition & Summarization API',
    'uiversion': 3,
    'openapi': '3.0.2',
    # 'specs_route': '/apidocs/' # Если хочешь кастомный URL
}
# Указываем Flasgger искать YAML-файлы в папке 'docs'
swagger = Swagger(app, template_file='docs/process.yml') 

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'm4a'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Убедимся, что папка uploads находится внутри папки app
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), UPLOAD_FOLDER), exist_ok=True)

# --- Наша "база данных" в памяти ---
tasks = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- API Endpoints ---

@app.route('/process', methods=['POST'])
@swag_from('docs/process.yml')
def process_audio():
    if 'audio_file' not in request.files:
        return jsonify({"error": "No audio_file part"}), 400
    file = request.files['audio_file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "Invalid or no selected file"}), 400

    task_id = str(uuid.uuid4())
    filename = secure_filename(f"{task_id}_{file.filename}")
    # Сохраняем файл в папку app/uploads/
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), UPLOAD_FOLDER, filename)
    file.save(filepath)

    tasks[task_id] = {"status": "processing", "result": None}

    # =================================================================
    # ПОКА ЧТО ДЕЛАЕМ СИНХРОННО ПРЯМО ЗДЕСЬ
    # В будущем этот блок кода переедет в Celery Worker
    # =================================================================
    transcription_result = run_transcription(filepath)
    os.remove(filepath) # Удаляем временный файл

    if transcription_result:
        tasks[task_id]['status'] = 'completed'
        tasks[task_id]['result'] = transcription_result
    else:
        tasks[task_id]['status'] = 'failed'
        tasks[task_id]['result'] = {"error": "Failed to transcribe the audio."}
    
    # Сразу возвращаем task_id, хотя задача уже выполнена
    return jsonify({"message": "Task received and processed", "task_id": task_id}), 202


@app.route('/status/<string:task_id>', methods=['GET'])
@swag_from('docs/status.yml')
def get_status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"task_id": task_id, "status": task['status']})


@app.route('/result/<string:task_id>', methods=['GET'])
@swag_from('docs/result.yml')
def get_result(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    if task['status'] != 'completed':
        return jsonify({"message": f"Task status is: {task['status']}"}), 202
    
    return jsonify(task['result'])