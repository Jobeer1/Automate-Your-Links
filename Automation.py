import tkinter as tk
from tkinter import messagebox, simpledialog
import pyautogui
import time
import threading
from pynput import mouse

class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_click_task(self, x, y, delay):
        self.tasks.append(("click", x, y, delay))

    def add_hotkey_task(self, hotkey, delay):
        self.tasks.append(("hotkey", hotkey, delay))

    def add_move_task(self, start_x, start_y, end_x, end_y, delay):
        self.tasks.append(("move", start_x, start_y, end_x, end_y, delay))

    def get_tasks(self):
        return self.tasks

    def clear_tasks(self):
        self.tasks.clear()

    def remove_task(self, index):
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
        else:
            messagebox.showerror("Error", "Invalid task index.")
class TaskExecutor:
    def __init__(self, task_manager):
        self.task_manager = task_manager
        self.running = False
        self.task_thread = None
        self.paused = False  # Add a paused state

    def start_tasks(self):
        self.running = True
        self.paused = False  # Ensure not paused when starting
        self.task_thread = threading.Thread(target=self.execute_tasks)
        self.task_thread.start()

    def stop_tasks(self):
        self.running = False
        self.paused = False # Ensure not paused when stopping
        if self.task_thread and self.task_thread.is_alive():
            self.task_thread.join()

    def pause_tasks(self): # Pause the execution of tasks
        self.paused = True

    def resume_tasks(self): # Resume the execution of tasks
        self.paused = False

    def execute_tasks(self):
        while self.running:
            for task in self.task_manager.get_tasks():
                if not self.running:
                    break

                while self.paused and self.running: # Check if paused and still running
                    time.sleep(1) # Small delay to avoid busy-waiting

                if not self.running: # Check running state again after possible pause
                    break

                task_type = task[0]
                try:
                    if task_type == "click":
                        x, y, delay = task[1], task[2], task[3]
                        time.sleep(delay)
                        pyautogui.click(x, y)
                    elif task_type == "hotkey":
                        hotkey, delay = task[1], task[2]
                        time.sleep(delay)
                        keys = hotkey.split('+')
                        pyautogui.hotkey(*keys)
                    elif task_type == "move":
                        start_x, start_y, end_x, end_y, delay = task[1], task[2], task[3], task[4], task[5]
                        time.sleep(delay)
                        pyautogui.moveTo(start_x, start_y)
                        pyautogui.dragTo(end_x, end_y, duration=1)
                except Exception as e:
                    print(f"Error executing {task_type} task: {str(e)}")
            time.sleep(0.1)  # Reduced sleep time for responsiveness

class AutomationApp:
    def __init__(self, root):
        self.root = root
        self.task_manager = TaskManager()
        self.task_executor = TaskExecutor(self.task_manager)
        self.create_ui()

    def create_ui(self):
        self.btn_add_task = tk.Button(self.root, text="Add Task", command=self.add_task)
        self.btn_add_task.pack()

        self.btn_start_tasks = tk.Button(self.root, text="Start Tasks", command=self.start_tasks)
        self.btn_start_tasks.pack()

        self.btn_stop_tasks = tk.Button(self.root, text="Stop Tasks", command=self.stop_tasks)
        self.btn_stop_tasks.pack()

        self.btn_pause_tasks = tk.Button(self.root, text="Pause Tasks", command=self.pause_tasks)
        self.btn_pause_tasks.pack()

        self.btn_resume_tasks = tk.Button(self.root, text="Resume Tasks", command=self.resume_tasks)
        self.btn_resume_tasks.pack()

        self.tasks_frame = tk.Frame(self.root)
        self.tasks_frame.pack()

        self.status_label = tk.Label(self.root, text="Status: Idle")
        self.status_label.pack()

    def update_status(self, message):
        self.status_label.config(text=f"Status: {message}")

    def add_task(self):
        task_type = simpledialog.askstring("Input", "Enter task type (click/hotkey/move):")
        if task_type is None:  # Handle cancel button press
            return

        task_type = task_type.lower()
        if task_type == "click":
            x, y = self.capture_mouse_position("Click the screen to capture the X and Y coordinates for click")
            if x is None:  # Handle cancel button press
                return
            delay = simpledialog.askfloat("Input", "Enter delay before task (seconds):", initialvalue=1.0)
            if delay is None:  # Handle cancel button press
                return
            self.task_manager.add_click_task(x, y, delay)
        elif task_type == "hotkey":
            hotkey = simpledialog.askstring("Input", "Enter hotkeys (e.g., ctrl+c):")
            if hotkey is None:  # Handle cancel button press
                return
            delay = simpledialog.askfloat("Input", "Enter delay before task (seconds):", initialvalue=1.0)
            if delay is None:  # Handle cancel button press
                return
            self.task_manager.add_hotkey_task(hotkey, delay)
        elif task_type == "move":
            start_x, start_y = self.capture_mouse_position("Click the screen to capture the starting X and Y coordinates for move")
            if start_x is None:  # Handle cancel button press
                return
            end_x, end_y = self.capture_mouse_position("Click the screen to capture the ending X and Y coordinates for move")
            if end_x is None:  # Handle cancel button press
                return
            delay = simpledialog.askfloat("Input", "Enter delay before task (seconds):", initialvalue=1.0)
            if delay is None:  # Handle cancel button press
                return
            self.task_manager.add_move_task(start_x, start_y, end_x, end_y, delay)

        self.update_task_list()

    def capture_mouse_position(self, message):
        messagebox.showinfo("Capture Position", message)
        position = None

        def on_click(x, y, button, pressed):
            nonlocal position
            if pressed:
                position = (x, y)
                return False

        with mouse.Listener(on_click=on_click) as listener:
            listener.join()

        return position

    def update_task_list(self):
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()

        for idx, task in enumerate(self.task_manager.get_tasks()):
            task_text = f"{idx+1}. {task[0].capitalize()} - "
            if task[0] == "click":
                task_text += f"X: {task[1]}, Y: {task[2]}, Delay: {task[3]}s"
            elif task[0] == "hotkey":
                task_text += f"Hotkeys: {task[1]}, Delay: {task[2]}s"
            elif task[0] == "move":
                task_text += f"Start X: {task[1]}, Start Y: {task[2]}, End X: {task[3]}, End Y: {task[4]}, Delay: {task[5]}s"

            label = tk.Label(self.tasks_frame, text=task_text)
            label.grid(row=idx, column=0, sticky="w")

            remove_button = tk.Button(self.tasks_frame, text="Remove", command=lambda i=idx: self.remove_task(i))
            remove_button.grid(row=idx, column=1)

    def remove_task(self, index):
        self.task_manager.remove_task(index)
        self.update_task_list()

    def start_tasks(self):
        self.update_status("Starting tasks")
        self.task_executor.start_tasks()

    def stop_tasks(self):
        self.update_status("Stopping tasks")
        self.task_executor.stop_tasks()

    def pause_tasks(self):
        self.update_status("Pausing tasks")
        self.task_executor.pause_tasks()

    def resume_tasks(self):
        self.update_status("Resuming tasks")
        self.task_executor.resume_tasks()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("500x300")
    app = AutomationApp(root)
    root.mainloop()  # This is the main loop!