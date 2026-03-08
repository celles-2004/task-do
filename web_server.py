from flask import Flask, jsonify, request, send_file
import json
import os

app = Flask(__name__)
TASKS_FILE = 'tasks.json'

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r', encoding='UTF-8') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

# Главная страница – отдаём HTML-интерфейс
@app.route('/')
def index():
    return send_file('index.html')

# API: получить все задачи
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = load_tasks()
    return jsonify(tasks)

# API: обновить задачи (полная замена)
@app.route('/api/tasks', methods=['POST'])
def update_tasks():
    new_tasks = request.get_json()
    if new_tasks is not None:
        save_tasks(new_tasks)
        return jsonify({'status': 'ok', 'tasks': new_tasks})
    return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=17789, debug=True)