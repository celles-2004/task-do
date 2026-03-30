import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import socket
import json
import os

# Цвета для тёмной темы
DARK_BG = "#2b2b2b"
DARK_FG = "#ffffff"
DARK_ENTRY_BG = "#3c3c3c"
DARK_ENTRY_FG = "#ffffff"
DARK_LIST_BG = "#3c3c3c"
DARK_LIST_FG = "#ffffff"
DARK_BUTTON_BG = "#404040"
DARK_BUTTON_FG = "#ffffff"
DARK_BUTTON_ACTIVE = "#4d4d4d"

# Цвета для светлой темы
LIGHT_BG = "#f0f0f0"
LIGHT_FG = "#000000"
LIGHT_ENTRY_BG = "#ffffff"
LIGHT_ENTRY_FG = "#000000"
LIGHT_LIST_BG = "#ffffff"
LIGHT_LIST_FG = "#000000"
LIGHT_BUTTON_BG = "#e1e1e1"
LIGHT_BUTTON_FG = "#000000"
LIGHT_BUTTON_ACTIVE = "#d5d5d5"

dark_mode = True

# Глобальные переменные для счётчиков действий
day_count = 0
total_count = 0

# Файл для локального хранения задач (синхронизируемый)
LOCAL_TASKS_FILE = "tasks.json"
# Базовая папка для хранения дневных логов
APP_NAME = "List_events"
BASE_DIR = os.path.join(os.getcwd(), APP_NAME)

# --- Работа с папками и файлами даты ---
def get_today_str():
    return datetime.now().strftime("%Y.%m.%d")

def get_today_dir():
    today = get_today_str()
    path = os.path.join(BASE_DIR, today)
    os.makedirs(path, exist_ok=True)
    return path

def get_day_count_file():
    return os.path.join(get_today_dir(), f"{get_today_str()} count per day.txt")

def get_day_list_file():
    return os.path.join(get_today_dir(), f"{get_today_str()} list per day.txt")

def get_total_count_file():
    return os.path.join(BASE_DIR, "total_count.txt")

# --- Инициализация и проверка нового дня ---
def check_new_day():
    """Если день сменился, очистить список и сбросить счётчики."""
    global day_count, total_count
    today = get_today_str()
    if not os.path.exists(get_today_dir()):
        clear_task_list()
        read_counters_from_files()
        update_action_counters()

def clear_task_list():
    """Очистить список задач в интерфейсе и в tasks.json."""
    listbox_tasks.delete(0, tk.END)
    save_local_tasks()
    update_day_list_file()

def read_counters_from_files():
    """Прочитать счётчики из файлов сегодняшнего дня (или создать)."""
    global day_count, total_count
    try:
        with open(get_day_count_file(), "r", encoding="utf-8") as f:
            day_count = int(f.read().strip())
    except FileNotFoundError:
        day_count = 0
        save_counters()

    try:
        with open(get_total_count_file(), "r", encoding="utf-8") as f:
            total_count = int(f.read().strip())
    except FileNotFoundError:
        total_count = 0
        save_counters()

def save_counters():
    """Сохраняет текущие значения счётчиков в файлы."""
    with open(get_day_count_file(), "w", encoding="utf-8") as f:
        f.write(f"{day_count:03d}")
    with open(get_total_count_file(), "w", encoding="utf-8") as f:
        f.write(f"{total_count:04d}")

def update_action_counters():
    day_counter_label.config(text=f"Действий сегодня: {day_count:03d}")
    total_counter_label.config(text=f"Всего действий: {total_count:04d}")

def recalc_day_count():
    """Пересчитывает day_count как количество задач с сегодняшней датой."""
    global day_count
    today_str = datetime.now().strftime("%Y-%m-%d")
    tasks = list(listbox_tasks.get(0, tk.END))
    day_count = sum(1 for task in tasks if task.startswith(today_str))
    save_counters()
    update_action_counters()

def update_day_list_file():
    """Перезаписать файл списка задач за сегодня актуальным списком из listbox."""
    tasks = list(listbox_tasks.get(0, tk.END))
    with open(get_day_list_file(), "w", encoding="utf-8") as f:
        for task in tasks:
            f.write(task + "\n")

# --- Работа с tasks.json ---
def save_local_tasks():
    tasks = list(listbox_tasks.get(0, tk.END))
    with open(LOCAL_TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def load_local_tasks():
    if os.path.exists(LOCAL_TASKS_FILE):
        try:
            with open(LOCAL_TASKS_FILE, "r", encoding="utf-8") as f:
                tasks = json.load(f)
            if not isinstance(tasks, list):
                messagebox.showerror("Ошибка", f"Файл {LOCAL_TASKS_FILE} содержит некорректные данные.")
                return
            update_listbox_from_list(tasks)
            recalc_day_count()  # day_count пересчитывается
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить задачи: {e}")

# --- Обработчики кнопок ---
def add_task(event=None):
    check_new_day()
    task = entry_task.get().strip()
    if task:
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")
        full_task = f"{date_str} {time_str} {task}"
        listbox_tasks.insert(tk.END, full_task)
        entry_task.delete(0, tk.END)

        global day_count, total_count
        day_count += 1
        total_count += 1
        save_counters()

        save_local_tasks()
        update_day_list_file()
        update_action_counters()
    else:
        messagebox.showwarning("", "Введите название задачи.")

def delete_task():
    check_new_day()
    try:
        selected_index = listbox_tasks.curselection()[0]
        task = listbox_tasks.get(selected_index)
        task_date = task[:10]  # YYYY-MM-DD
        today_str = datetime.now().strftime("%Y-%m-%d")

        listbox_tasks.delete(selected_index)

        global day_count, total_count
        if task_date == today_str:
            day_count = max(0, day_count - 1)
            # total_count не меняется
            save_counters()

        save_local_tasks()
        update_day_list_file()
        update_action_counters()
    except IndexError:
        messagebox.showwarning("Предупреждение", "Выберите задачу для удаления.")

# --- Синхронизация с сервером ---
SERVER_PORT = 17789
auto_sync_enabled = False

def load_from_server():
    server_ip = entry_server_ip.get().strip()
    if not server_ip:
        messagebox.showwarning("Предупреждение", "Введите IP сервера")
        return
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((server_ip, SERVER_PORT))
        client.sendall("GET".encode('utf-8'))
        data = client.recv(65536).decode('utf-8')
        tasks = json.loads(data)
        if not isinstance(tasks, list):
            messagebox.showerror("Ошибка", "Сервер вернул некорректные данные.")
            return
        update_listbox_from_list(tasks)
        messagebox.showinfo("Синхронизация", "Список загружен с сервера")
        save_local_tasks()
        recalc_day_count()  # обновляем day_count, total не трогаем
        update_day_list_file()
        check_new_day()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось подключиться к серверу: {e}")
    finally:
        client.close()

def send_to_server():
    server_ip = entry_server_ip.get().strip()
    if not server_ip:
        messagebox.showwarning("Предупреждение", "Введите IP сервера")
        return
    try:
        local_tasks = list(listbox_tasks.get(0, tk.END))
        data = "SET:" + json.dumps(local_tasks, ensure_ascii=False)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((server_ip, SERVER_PORT))
        client.sendall(data.encode('utf-8'))
        response = client.recv(65536).decode('utf-8')
        updated_tasks = json.loads(response)
        update_listbox_from_list(updated_tasks)
        messagebox.showinfo("Синхронизация", "Список отправлен и обновлён")
        save_local_tasks()
        recalc_day_count()  # обновляем day_count, total не трогаем
        update_day_list_file()
        check_new_day()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось отправить: {e}")
    finally:
        client.close()

def update_listbox_from_list(task_list):
    listbox_tasks.delete(0, tk.END)
    for task in task_list:
        listbox_tasks.insert(tk.END, task)

def toggle_auto_sync():
    global auto_sync_enabled
    auto_sync_enabled = auto_sync_var.get()
    if auto_sync_enabled:
        auto_sync()

def auto_sync():
    if not auto_sync_enabled:
        return
    client = None
    try:
        server_ip = entry_server_ip.get().strip()
        if server_ip:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(5)
            client.connect((server_ip, SERVER_PORT))
            client.sendall("GET".encode('utf-8'))
            data = client.recv(65536).decode('utf-8')
            tasks = json.loads(data)
            if not isinstance(tasks, list):
                return
            current_tasks = list(listbox_tasks.get(0, tk.END))
            if tasks != current_tasks:
                update_listbox_from_list(tasks)
                save_local_tasks()
                recalc_day_count()  # обновляем day_count
                update_day_list_file()
                check_new_day()
    except Exception:
        pass
    finally:
        if client:
            client.close()
        if auto_sync_enabled:
            root.after(10000, auto_sync)

# --- Тема (без изменений) ---
def apply_theme():
    global dark_mode
    if dark_mode:
        bg_color = DARK_BG
        fg_color = DARK_FG
        entry_bg = DARK_ENTRY_BG
        entry_fg = DARK_ENTRY_FG
        list_bg = DARK_LIST_BG
        list_fg = DARK_LIST_FG
        button_bg = DARK_BUTTON_BG
        button_fg = DARK_BUTTON_FG
        button_active = DARK_BUTTON_ACTIVE
    else:
        bg_color = LIGHT_BG
        fg_color = LIGHT_FG
        entry_bg = LIGHT_ENTRY_BG
        entry_fg = LIGHT_ENTRY_FG
        list_bg = LIGHT_LIST_BG
        list_fg = LIGHT_LIST_FG
        button_bg = LIGHT_BUTTON_BG
        button_fg = LIGHT_BUTTON_FG
        button_active = LIGHT_BUTTON_ACTIVE

    root.config(bg=bg_color)
    entry_task.config(bg=entry_bg, fg=entry_fg, insertbackground=fg_color)
    listbox_tasks.config(bg=list_bg, fg=list_fg, selectbackground=button_active)
    day_counter_label.config(bg=bg_color, fg=fg_color)
    total_counter_label.config(bg=bg_color, fg=fg_color)
    frame_list.config(bg=bg_color)

    for btn in [btn_add, btn_delete, btn_exit, btn_toggle_theme, btn_load, btn_send]:
        btn.config(bg=button_bg, fg=button_fg, activebackground=button_active)

    frame_sync.config(bg=bg_color)
    label_ip.config(bg=bg_color, fg=fg_color)
    entry_server_ip.config(bg=entry_bg, fg=entry_fg, insertbackground=fg_color)
    chk_auto_sync.config(bg=bg_color, fg=fg_color, selectcolor=button_bg, activebackground=button_active)

def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    apply_theme()

# --- Создание GUI ---
root = tk.Tk()
root.title("Список дел")
root.update_idletasks()
root.geometry('')
root.resizable(True, True)

root.after(10000, auto_sync)

entry_task = tk.Entry(root, width=40)
entry_task.pack(pady=10)
entry_task.bind("<Return>", add_task)

btn_add = tk.Button(root, text="Добавить действие", command=add_task)
btn_add.pack()

frame_list = tk.Frame(root)
frame_list.pack(pady=10, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(frame_list)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox_tasks = tk.Listbox(
    frame_list,
    width=60,
    height=15,
    yscrollcommand=scrollbar.set,
    selectmode=tk.SINGLE
)
listbox_tasks.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=listbox_tasks.yview)

btn_delete = tk.Button(root, text="Удалить действие", command=delete_task)
btn_delete.pack(pady=2)

day_counter_label = tk.Label(root, text="000", font=("Arial", 10))
day_counter_label.pack()
total_counter_label = tk.Label(root, text="0000", font=("Arial", 10))
total_counter_label.pack(pady=(0,10))

btn_toggle_theme = tk.Button(root, text="Переключить тему", command=toggle_theme)
btn_toggle_theme.pack(pady=2)

frame_sync = tk.Frame(root)
frame_sync.pack(pady=5)

btn_load = tk.Button(frame_sync, text="Загрузить", command=load_from_server)
btn_load.pack(side=tk.LEFT, padx=2)

btn_send = tk.Button(frame_sync, text="Отправить", command=send_to_server)
btn_send.pack(side=tk.LEFT, padx=2)

label_ip = tk.Label(frame_sync, text="IP сервера:")
label_ip.pack(side=tk.LEFT, padx=5)

entry_server_ip = tk.Entry(frame_sync, width=15)
entry_server_ip.insert(0, "192.168.1.40")
entry_server_ip.pack(side=tk.LEFT, padx=5)

auto_sync_var = tk.BooleanVar(value=False)
chk_auto_sync = tk.Checkbutton(frame_sync, text="Авто", variable=auto_sync_var, command=toggle_auto_sync)
chk_auto_sync.pack(side=tk.LEFT, padx=5)

btn_exit = tk.Button(root, text="Выход", command=root.quit)
btn_exit.pack(pady=5)

apply_theme()
read_counters_from_files()
check_new_day()
load_local_tasks()
update_action_counters()
update_day_list_file()

root.mainloop()