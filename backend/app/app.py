import os
import uuid
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS  # <-- Убедись, что CORS импортирован
from werkzeug.utils import secure_filename

# Импортируем наши "движки"
from whisper_transcriber import run_transcription
from summarizer import get_available_types

# --- Настройка путей для работы с React-сборкой ---
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
# Путь к папке static немного отличается, т.к. Vite создает подпапку assets
STATIC_FOLDER = os.path.join(APP_ROOT, 'static')
TEMPLATE_FOLDER = os.path.join(APP_ROOT, 'templates')

app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)
CORS(app) # <-- Включаем CORS для всего приложения

# --- Настройка папки для загрузок ---
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

tasks = {} # Временное хранилище задач в памяти

def allowed_file(filename):
    """Проверяет, что расширение файла разрешено."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'wav', 'mp3', 'ogg', 'm4a'}

# --- РУЧКИ (ЭНДПОИНТЫ) ---

# Эта ручка будет отдавать наш фронтенд (index.html и статику вроде JS/CSS)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # Эта логика нужна, чтобы React Router (если он используется) работал правильно.
    # Если запрашивается существующий файл из папки static, отдаем его.
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # Во всех остальных случаях отдаем главный index.html, а React сам разберется с роутингом.
        return send_from_directory(app.template_folder, 'index.html')
        
# --- API для общения с фронтендом ---
# Важно: URL начинаются с /api/, чтобы не конфликтовать с путями фронтенда

@app.route('/api/summarization-types', methods=['GET'])
def summarization_types():
    """Отдает фронтенду список доступных типов суммаризации."""
    return jsonify(get_available_types())

@app.route('/api/process', methods=['POST'])
def process_audio():
    """Принимает файл, ставит его в "очередь" и запускает обработку."""
    if 'audio_file' not in request.files:
        return jsonify({"error": "No audio_file part"}), 400
    
    file = request.files['audio_file']
    
    # ИСПРАВЛЕНО: Читаем поле 'compression_level', которое присылает твой фронтенд
    summary_type = (
        request.form.get('type') or           # Стандартное название
        request.form.get('summary_type') or   # Альтернативное название
        request.form.get('compression_level') or  # Старое название
        request.form.get('summarization_type') or # Ещё один вариант
        'brief'  # По умолчанию
    )

    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file or file type"}), 400

    task_id = str(uuid.uuid4())
    filename = secure_filename(f"{task_id}_{file.filename}")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    tasks[task_id] = {"status": "processing", "result": None}

    # В будущем этот блок переедет в Celery Worker
    transcription_result = run_transcription(filepath, summary_type)
    os.remove(filepath) # Удаляем временный файл после обработки

    if transcription_result:
        tasks[task_id]['status'] = 'completed'
        tasks[task_id]['result'] = transcription_result
    else:
        tasks[task_id]['status'] = 'failed'
    
    return jsonify({"message": "Task received", "task_id": task_id}), 202

@app.route('/api/status/<string:task_id>', methods=['GET'])
def get_status(task_id):
    """Проверяет статус задачи по ее ID."""
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"task_id": task_id, "status": task['status']})

@app.route('/api/result/<string:task_id>', methods=['GET'])
def get_result(task_id):
    """Возвращает финальный результат обработанной задачи."""
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    if task['status'] == 'completed':
        return jsonify(task.get('result'))
    elif task['status'] == 'failed':
         return jsonify({"error": "Task processing failed"}), 500
    else: # status is 'processing'
        return jsonify({"message": f"Task status is: {task['status']}"}), 202