import os
import uuid
from flask import Flask, request, jsonify
from flasgger import Swagger, swag_from
from werkzeug.utils import secure_filename

# --- 1. Настройка приложения Flask и Swagger ---
app = Flask(__name__)
# Добавляем немного конфигурации для Swagger
app.config['SWAGGER'] = {
    'title': 'Speech Recognition & Summarization API',
    'uiversion': 3,
    'openapi': '3.0.2',
    'doc_dir': './docs/'
}
swagger = Swagger(app)

# --- 2. Настройка для загрузки файлов ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'm4a'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Проверяем, что папка для загрузок существует
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- 3. "База данных" в памяти для эмуляции ---
# В реальном проекте здесь будет Redis/Celery и PostgreSQL/MongoDB
tasks = {}

def allowed_file(filename):
    """Проверяет, что у файла разрешенное расширение."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- 4. Определяем наши API ручки (endpoints) ---

@app.route('/process', methods=['POST'])
@swag_from('docs/process.yml')
def process_audio():
    """
    Принимает аудиофайл и ставит его в очередь на обработку.
    """
    if 'audio_file' not in request.files:
        return jsonify({"error": "No audio_file part in the request"}), 400

    file = request.files['audio_file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        # Генерируем уникальный ID для нашей задачи
        task_id = str(uuid.uuid4())
        filename = secure_filename(f"{task_id}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Сохраняем информацию о задаче в нашу "базу"
        tasks[task_id] = {
            "status": "processing",
            "original_filename": file.filename,
            "stored_path": filepath,
            "transcription": None,
            "summary": None
        }

        # В реальном приложении здесь бы мы отправили задачу в Celery/Kafka
        # worker.apply_async(args=[task_id, filepath])
        
        # Для демо эмулируем завершение задачи через некоторое время
        # Просто для примера, чтобы было что проверять
        if len(tasks) % 2 == 0: # Каждую вторую задачу "завершаем" для примера
            tasks[task_id]['status'] = 'completed'
            tasks[task_id]['transcription'] = 'Это пример расшифрованного текста из аудиофайла. LLM отлично справляются с такими задачами.'
            tasks[task_id]['summary'] = 'Аудио расшифровано, результат хороший.'

        # Возвращаем 202 Accepted, т.к. задача принята, но еще не выполнена
        return jsonify({"message": "File accepted for processing", "task_id": task_id}), 202

    return jsonify({"error": "File type not allowed"}), 400


@app.route('/status/<string:task_id>', methods=['GET'])
@swag_from('docs/status.yml')
def get_status(task_id):
    """
    Проверяет статус задачи по её ID.
    """
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({"task_id": task_id, "status": task['status']})


@app.route('/result/<string:task_id>', methods=['GET'])
@swag_from('docs/result.yml')
def get_result(task_id):
    """
    Возвращает результат обработки задачи по её ID.
    """
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    if task['status'] != 'completed':
        return jsonify({"message": "Task is still processing", "status": task['status']}), 202

    return jsonify({
        "task_id": task_id,
        "status": task['status'],
        "transcription": task['transcription'],
        "summary": task['summary']
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)