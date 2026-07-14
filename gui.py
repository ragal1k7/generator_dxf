import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from generator import generate_box


# ---------------- Проверка данных ----------------

def validate(length, width, height, thickness):

    if length <= 0:
        return "Длина должна быть больше 0."

    if width <= 0:
        return "Ширина должна быть больше 0."

    if height <= 0:
        return "Высота должна быть больше 0."

    if thickness <= 0:
        return "Толщина должна быть больше 0."

    if thickness >= min(length, width, height) / 2:
        return "Толщина слишком большая."

    return None


# ---------------- Генерация ----------------

def generate():

    try:

        length = float(entry_length.get())
        width = float(entry_width.get())
        height = float(entry_height.get())
        thickness = float(entry_thickness.get())

    except ValueError:

        messagebox.showerror("Ошибка", "Все значения должны быть числами.")
        return

    error = validate(length, width, height, thickness)

    if error:

        messagebox.showerror("Ошибка", error)
        return

    filename = filedialog.asksaveasfilename(
        defaultextension=".dxf",
        filetypes=[("DXF", "*.dxf")]
    )

    if not filename:
        return

    slot_length = 10

    try:

        generate_box(
            length,
            width,
            height,
            thickness,
            slot_length,
            filename=filename
        )

        status.config(
            text=f"✔ Файл успешно сохранён\nДлина паза: {slot_length:.2f} мм",
            foreground="green"
        )

    except Exception as e:

        messagebox.showerror("Ошибка", str(e))


# ---------------- GUI ----------------

def run_gui():

    global entry_length
    global entry_width
    global entry_height
    global entry_thickness
    global status

    root = tk.Tk()

    root.title("Генератор коробок")

    root.geometry("300x300")

    root.resizable(False, False)

    pad = 8

    ttk.Label(root, text="Длина (мм)").pack(pady=(15, 0))
    entry_length = ttk.Entry(root)
    entry_length.insert(0, "160")
    entry_length.pack()

    ttk.Label(root, text="Ширина (мм)").pack(pady=(10, 0))
    entry_width = ttk.Entry(root)
    entry_width.insert(0, "110")
    entry_width.pack()

    ttk.Label(root, text="Высота (мм)").pack(pady=(10, 0))
    entry_height = ttk.Entry(root)
    entry_height.insert(0, "60")
    entry_height.pack()

    ttk.Label(root, text="Толщина материала (мм)").pack(pady=(10, 0))
    entry_thickness = ttk.Entry(root)
    entry_thickness.insert(0, "4")
    entry_thickness.pack()

    ttk.Button(
        root,
        text="Сгенерировать DXF",
        command=generate
    ).pack(
        pady=20
    )

    status = ttk.Label(root, text="")
    status.pack()

    root.mainloop()