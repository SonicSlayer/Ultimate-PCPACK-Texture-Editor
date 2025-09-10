import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, END, Label, PhotoImage
from PIL import Image, ImageTk
import os
import io

DDS_CHUNK_SIZE = 65536
DDS_SIGNATURE = b'DDS '

class PCPackTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultimate Spider-Man PCPACK Tool")

        self.dds_offsets = []
        self.file_data = b''
        self.filename = None

        self.load_button = tk.Button(root, text="Открыть .PCPACK", command=self.load_pcpack)
        self.load_button.pack(pady=5)

        self.listbox = Listbox(root, width=50)
        self.listbox.pack(pady=5)
        self.listbox.bind('<<ListboxSelect>>', self.preview_dds)

        self.preview_label = Label(root, text="Предпросмотр DDS:")
        self.preview_label.pack(pady=(10, 0))
        self.image_label = Label(root)
        self.image_label.pack(pady=5)

        self.extract_button = tk.Button(root, text="Извлечь выбранную DDS", command=self.extract_dds)
        self.extract_button.pack(pady=5)

        self.replace_button = tk.Button(root, text="Заменить выбранную DDS", command=self.replace_dds)
        self.replace_button.pack(pady=5)

    def load_pcpack(self):
        file_path = filedialog.askopenfilename(filetypes=[("PCPACK files", "*.PCPACK")])
        if not file_path:
            return

        with open(file_path, 'rb') as f:
            self.file_data = bytearray(f.read()) 

        self.filename = os.path.basename(file_path)
        self.dds_offsets = self.find_dds_offsets(self.file_data)

        self.listbox.delete(0, END)
        for i, offset in enumerate(self.dds_offsets):
            self.listbox.insert(END, f"DDS #{i+1} @ 0x{offset:X}")

        messagebox.showinfo("Успешно", f"Найдено DDS: {len(self.dds_offsets)}")

    def find_dds_offsets(self, data):
        offsets = []
        idx = 0
        while idx < len(data):
            idx = data.find(DDS_SIGNATURE, idx)
            if idx == -1:
                break
            offsets.append(idx)
            idx += 4  # Пропустить сигнатуру
        return offsets

    def extract_dds(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Не выбрано", "Выберите DDS для извлечения")
            return

        index = selection[0]
        offset = self.dds_offsets[index]
        dds_data = self.file_data[offset:offset + DDS_CHUNK_SIZE]

        save_path = filedialog.asksaveasfilename(defaultextension=".dds", filetypes=[("DDS files", "*.dds")])
        if save_path:
            with open(save_path, 'wb') as f:
                f.write(dds_data)
            messagebox.showinfo("Готово", f"Сохранено: {save_path}")

    def replace_dds(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Не выбрано", "Выберите DDS для замены")
            return

        index = selection[0]
        offset = self.dds_offsets[index]

        file_path = filedialog.askopenfilename(filetypes=[("DDS files", "*.dds")])
        if not file_path:
            return

        with open(file_path, 'rb') as f:
            new_dds = f.read()

        if len(new_dds) > DDS_CHUNK_SIZE:
            messagebox.showerror("Ошибка", f"DDS слишком большой (максимум {DDS_CHUNK_SIZE} байт)")
            return

        self.file_data[offset:offset + len(new_dds)] = new_dds

        save_path = filedialog.asksaveasfilename(defaultextension=".PCPACK", filetypes=[("PCPACK files", "*.PCPACK")])
        if save_path:
            with open(save_path, 'wb') as f:
                f.write(self.file_data)
            messagebox.showinfo("Готово", f"Сохранено: {save_path}")

    def preview_dds(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        offset = self.dds_offsets[index]
        dds_data = self.file_data[offset:offset + DDS_CHUNK_SIZE]

        try:
            with Image.open(io.BytesIO(dds_data)) as img:
                img = img.convert("RGB")
                img.thumbnail((256, 256))
                tk_img = ImageTk.PhotoImage(img)
                self.image_label.config(image=tk_img)
                self.image_label.image = tk_img
        except Exception as e:
            self.image_label.config(image='', text="Не удалось отобразить")
            print("Предпросмотр DDS не удался:", e)

if __name__ == '__main__':
    root = tk.Tk()
    app = PCPackTool(root)
    root.mainloop()