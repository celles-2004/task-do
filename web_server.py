from flask import Flask, jsonify, request, send_file
import json
import os
from datetime import datetime

app = Flask(__name__)
TASKS_FILE = 'tasks.json'
APP_NAME = "List_events"
BASE_DIR = os.path.join(os.getcwd(), APP_NAME)

def get_today_str():
    return datetime.now().strftime("%Y.%m.%d")

def get_today_dir():
    today = get_today_str()
    path = os.path.join(BASE_DIR, today)
    os.makedirs(path, exist_ok=True)
    return path

def get_day_count_file():
    return os.path.join(get_today_dir(), f"{get_today_str()} count per day.txt")

def get_total_count_file():
    return os.path.join(BASE_DIR, "total_count.txt")

def read_counters():
    day = 0
    total = 0
    if os.path.exists(get_day_count_file()):
        with open(get_day_count_file(), 'r', encoding='utf-8') as f:
            day = int(f.read().strip())
    if os.path.exists(get_total_count_file()):
        with open(get_total_count_file(), 'r', encoding='utf-8') as f:
            total = int(f.read().strip())
    return day, total

def write_counters(day, total):
    with open(get_day_count_file(), 'w', encoding='utf-8') as f:
        f.write(f"{day:03d}")
    with open(get_total_count_file(), 'w', encoding='utf-8') as f:
        f.write(f"{total:04d}")

def update_day_list_file(tasks):
    day_list_file = os.path.join(get_today_dir(), f"{get_today_str()} list per day.txt")
    with open(day_list_file, "w", encoding="utf-8") as f:
        for task in tasks:
            f.write(task + "\n")

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r', encoding='UTF-8') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = load_tasks()
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def update_tasks():
    new_tasks = request.get_json()
    if new_tasks is None:
        return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

    old_tasks = load_tasks()
    set_old = set(old_tasks)
    set_new = set(new_tasks)
    added = list(set_new - set_old)
    removed = list(set_old - set_new)

    today_str = datetime.now().strftime("%Y-%m-%d")
    day_change = 0
    total_change = 0

    for task in added:
        total_change += 1
        if task.startswith(today_str):
            day_change += 1

    for task in removed:
        if task.startswith(today_str):
            day_change -= 1
            total_change -= 1
        # total не меняется при удалении

    if day_change != 0 or total_change != 0:
        day, total = read_counters()
        day = max(0, day + day_change)
        total = max(0, total + total_change)
        write_counters(day, total)

    save_tasks(new_tasks)
    update_day_list_file(new_tasks)
    return jsonify({'status': 'ok', 'tasks': new_tasks})

@app.route('/api/counters', methods=['GET'])
def counters():
    day, total = read_counters()
    return jsonify({
        'day': f"{day:03d}",
        'total': f"{total:04d}"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=17789, debug=True)