import os
import uuid
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from whisper_transcriber import run_transcription
from summarizer import get_available_types, ask_question_about_text

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_FOLDER = os.path.join(APP_ROOT, 'static')
TEMPLATE_FOLDER = os.path.join(APP_ROOT, 'templates')

app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)
CORS(app)

UPLOAD_FOLDER = os.path.join(APP_ROOT, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

tasks = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'wav', 'mp3', 'ogg', 'm4a'}

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.template_folder, 'index.html')

@app.route('/api/summarization-types', methods=['GET'])
def summarization_types():
    return jsonify(get_available_types())

@app.route('/api/process', methods=['POST'])
def process_audio():
    if 'audio_file' not in request.files: return jsonify({"error": "Файл не найден"}), 400
    file = request.files['audio_file']
    summary_type = request.form.get('compression_level', 'brief')
    # Получаем тему (domain/topic) из фронтенда
    topic = request.form.get('topic', 'general')

    if file.filename == '' or not allowed_file(file.filename): return jsonify({"error": "Неверный формат файла"}), 400

    task_id = str(uuid.uuid4())
    filename = secure_filename(f"{task_id}_{file.filename}")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    tasks[task_id] = {"status": "processing", "result": None}

    # Запускаем обработку (прокидываем тему в Whisper и LLM)
    res = run_transcription(filepath, summary_type, domain=topic)
    os.remove(filepath)

    if res:
        tasks[task_id]['status'] = 'completed'
        tasks[task_id]['result'] = res
    else:
        tasks[task_id]['status'] = 'failed'
    
    return jsonify({"task_id": task_id}), 202

@app.route('/api/status/<string:task_id>', methods=['GET'])
def get_status(task_id):
    task = tasks.get(task_id)
    if not task: return jsonify({"error": "Задача не найдена"}), 404
    return jsonify({"status": task['status']})

@app.route('/api/result/<string:task_id>', methods=['GET'])
def get_result(task_id):
    task = tasks.get(task_id)
    if not task or task['status'] != 'completed': return jsonify({"error": "Результат не готов"}), 404
    return jsonify(task['result'])

@app.route('/api/ask', methods=['POST'])
def ask_ai():
    """Новый эндпоинт для чата (Q&A)"""
    data = request.json
    text = data.get('text')
    question = data.get('question')
    
    if not text or not question:
        return jsonify({"error": "Нужен текст и вопрос"}), 400
    
    res = ask_question_about_text(text, question)
    return jsonify(res)

if __name__ == '__main__':
    app.run(debug=True, port=5000)