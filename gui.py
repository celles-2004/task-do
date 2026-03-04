import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import socket
import json

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

# Создание лог
LOG_FILE = datetime.now().strftime("%Y-%m-%d") + ".txt"

def log_action(action, task_text=""):
    """Записывает действие в лог-файл с временной меткой."""
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    with open(LOG_FILE,"a", encoding="utf-8") as f:
        if task_text:
            f.write(f"[{timestamp}] {action}: {task_text}\n")
        else:
            f.write(f"[{timestamp}] {action}\n")

# Тема
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
    counter_label.config(bg=bg_color, fg=fg_color)
    frame_list.config(bg=bg_color)

    for btn in [btn_add, btn_mark, btn_delete, btn_exit, btn_toggle_theme, btn_load, btn_send]:
        btn.config(bg=button_bg, fg=button_fg, activebackground=button_active)

    frame_sync.config(bg=bg_color)
    label_ip.config(bg=bg_color, fg=fg_color)
    entry_server_ip.config(bg=entry_bg, fg=entry_fg, insertbackground=fg_color)

def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    apply_theme()

def update_counter():
    total = listbox_tasks.size()
    completed = 0
    for i in range(total):
        task = listbox_tasks.get(i)
        if task.startswith("✔ "):
            completed += 1
    counter_label.config(text=f"Всего задач: {total}   Выполнено: {completed}")

def add_task(event=None):
    task = entry_task.get().strip()
    if task:
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
        full_task = f"[{timestamp}] {task}"
        listbox_tasks.insert(tk.END, full_task)
        entry_task.delete(0, tk.END)
        update_counter()
        log_action("ДОБАВЛЕНО", task)
    else:
        messagebox.showwarning("", "Введите название задачи.")

def delete_task():
    try:
        selected_index = listbox_tasks.curselection()[0]
        task = listbox_tasks.get(selected_index)  # получаем текст задачи
        
        # Очищаем от служебных символов для лога
        clean_task = task
        if clean_task.startswith("✔ "):
            clean_task = clean_task[2:]
        if clean_task.startswith("[") and "]" in clean_task:
            clean_task = clean_task.split("]", 1)[1].strip()
        
        listbox_tasks.delete(selected_index)      # удаляем задачу
        update_counter()
        log_action("УДАЛЕНО", clean_task)
    except IndexError:
        messagebox.showwarning("Предупреждение", "Выберите задачу для удаления.")

def mark_completed():
    try:
        selected_index = listbox_tasks.curselection()[0]
        task = listbox_tasks.get(selected_index)
        
        if task.startswith("✔ "):
            new_task = task[2:]          # снять отметку
            action = "СНЯТО ВЫПОЛНЕНИЕ"
        else:
            new_task = "✔ " + task       # поставить отметку
            action = "ВЫПОЛНЕНО"
        
        listbox_tasks.delete(selected_index)      # удаляем старую задачу
        listbox_tasks.insert(selected_index, new_task)  # вставляем новую
        update_counter()
        
        # Очищаем для лога
        clean_task = new_task
        if clean_task.startswith("✔ "):
            clean_task = clean_task[2:]
        if clean_task.startswith("[") and "]" in clean_task:
            clean_task = clean_task.split("]", 1)[1].strip()
        
        log_action(action, clean_task)
    except IndexError:
        messagebox.showwarning("Предупреждение", "Выберите задачу.")

SERVER_PORT = 5000

def load_from_server():
    """Запрашивает список задач с сервера и обновляет локальный."""
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
        update_listbox_from_list(tasks)
        messagebox.showinfo("Синхронизация", "Список загружен с сервера")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось подключиться к серверу: {e}")
    finally:
        client.close()

def send_to_server():
    """Отправляет текущий локальный список на сервер."""
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
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось отправить: {e}")
    finally:
        client.close()

def update_listbox_from_list(task_list):
    """Заменяет содержимое listbox на переданный список (вызывать в главном потоке)."""
    listbox_tasks.delete(0, tk.END)
    for task in task_list:
        listbox_tasks.insert(tk.END, task)
    update_counter()

# Создание главного окна
root = tk.Tk()
root.title("Список дел")
root.update_idletasks()
root.geometry('')
root.resizable(True, True)

# Поле ввода
entry_task = tk.Entry(root, width=40)
entry_task.pack(pady=10)
entry_task.bind("<Return>", add_task)

# Кнопка добавления
btn_add = tk.Button(root, text="Добавить задачу", command=add_task)
btn_add.pack()

# Список задач с прокруткой
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

# Кнопки управления
btn_mark = tk.Button(root, text="Отметить выполненной", command=mark_completed)
btn_mark.pack(pady=2)

btn_delete = tk.Button(root, text="Удалить задачу", command=delete_task)
btn_delete.pack(pady=2)

# Счётчик
counter_label = tk.Label(root, text="Всего задач: 0   Выполнено: 0", font=("Arial", 10))
counter_label.pack(pady=10)

# Кнопка переключения темы
btn_toggle_theme = tk.Button(root, text="Переключить тему", command=toggle_theme)
btn_toggle_theme.pack(pady=2)

# Рамка для синхронизации
frame_sync = tk.Frame(root)
frame_sync.pack(pady=5)

# Кнопки синхронизации с сервером
btn_load = tk.Button(frame_sync, text="Загрузить", command=load_from_server)
btn_load.pack(side=tk.LEFT, padx=2)

btn_send = tk.Button(frame_sync, text="Отправить", command=send_to_server)
btn_send.pack(side=tk.LEFT, padx=2)

label_ip = tk.Label(frame_sync, text="IP сервера:")
label_ip.pack(side=tk.LEFT, padx=5)

entry_server_ip = tk.Entry(frame_sync, width=15)
entry_server_ip.insert(0, "192.168.1.100")  # пример
entry_server_ip.pack(side=tk.LEFT, padx=5)


# Выход
btn_exit = tk.Button(root, text="Выход", command=root.quit)
btn_exit.pack(pady=5)

# Применяем начальную тему
apply_theme()

root.mainloop()