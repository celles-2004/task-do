import socket
import threading
import json
import os

HOST = '0.0.0.0'   # слушаем все интерфейсы
PORT = 17789
TASKS_FILE = 'tasks.json'

# Загружаем задачи из файла при старте
if os.path.exists(TASKS_FILE):
    with open(TASKS_FILE, 'r', encoding='utf-8') as f:
        tasks = json.load(f)
else:
    tasks = []

def save_tasks():
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def handle_client(conn, addr):
    global tasks
    print(f"Подключение от {addr}")
    try:
        data = conn.recv(65536).decode('utf-8').strip()
        if not data:
            return
        if data == "GET":
            # Отправляем текущий список
            response = json.dumps(tasks)
            conn.sendall(response.encode('utf-8'))
            print(f"Отправлен список задач клиенту {addr}")
        elif data.startswith("SET:"):
            # Получаем новый список от клиента
            new_tasks_str = data[4:]
            new_tasks = json.loads(new_tasks_str)
            # Объединяем (убираем дубликаты по строке)
            merged = list(set(tasks + new_tasks))
            # Сортируем по дате (если она в начале в формате [YYYY-MM-DD HH:MM])
            merged.sort()
            tasks = merged
            save_tasks()
            # Отправляем подтверждение и обновлённый список
            response = json.dumps(tasks)
            conn.sendall(response.encode('utf-8'))
            print(f"Получен список от {addr}, сохранено {len(tasks)} задач")
        else:
            print(f"Неизвестная команда: {data}")
    except Exception as e:
        print(f"Ошибка при обработке клиента {addr}: {e}")
    finally:
        conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Сервер запущен на {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()