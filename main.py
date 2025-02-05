import os
import fitz  # PyMuPDF
import pygame
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk

# 资源路径
BASE_PATH = "go"
PDF_PATH = os.path.join(BASE_PATH, "pdf")
MP3_PATH = os.path.join(BASE_PATH, "mp3")

# 处理MP3文件映射 {pdf_name: mp3_path}
def get_mp3_mapping():
    mp3_mapping = {}
    for folder in os.listdir(MP3_PATH):
        folder_path = os.path.join(MP3_PATH, folder)
        if os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                if file.endswith(".mp3"):
                    parts = file.split('.', 1)
                    if len(parts) == 2:
                        name = parts[1].replace(".mp3", "")
                        mp3_mapping[name] = os.path.join(folder_path, file)
    return mp3_mapping

MP3_MAPPING = get_mp3_mapping()

# 主应用类
class PDFPlayerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF & MP3 Player")
        self.geometry("800x600")

        self.current_folder = None
        self.current_pdf = None
        self.current_page = 0
        self.pdf_document = None
        self.audio_path = None

        self.init_home()

    # 初始化首页
    def init_home(self):
        self.clear_screen()
        tk.Label(self, text="请选择文件夹", font=("Arial", 16)).pack(pady=10)

        frame = tk.Frame(self)
        frame.pack(pady=10)

        for folder in sorted(os.listdir(PDF_PATH)):
            path = os.path.join(PDF_PATH, folder)
            if os.path.isdir(path):
                btn = tk.Button(frame, text=folder, command=lambda f=folder: self.show_pdf_list(f))
                btn.pack(side=tk.LEFT, padx=5)

    # 显示PDF列表
    def show_pdf_list(self, folder):
        self.current_folder = folder
        self.clear_screen()

        tk.Button(self, text="返回", command=self.init_home).pack(pady=10)

        listbox = tk.Listbox(self, width=50, height=20)
        listbox.pack(pady=10)

        pdf_folder = os.path.join(PDF_PATH, folder)
        pdf_files = [f[:-4] for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
        
        for pdf in sorted(pdf_files):
            listbox.insert(tk.END, pdf)

        def on_select(event):
            selected = listbox.curselection()
            if selected:
                pdf_name = listbox.get(selected[0])
                self.open_pdf(pdf_name)

        listbox.bind("<<ListboxSelect>>", on_select)

    # 打开PDF
    def open_pdf(self, pdf_name):
        self.current_pdf = pdf_name
        self.current_page = 0
        self.pdf_document = fitz.open(os.path.join(PDF_PATH, self.current_folder, pdf_name + ".pdf"))
        self.audio_path = MP3_MAPPING.get(pdf_name, None)
        self.show_pdf_page()

    # 显示PDF页面
    def show_pdf_page(self):
        if not self.pdf_document:
            return

        self.clear_screen()

        tk.Button(self, text="返回", command=lambda: self.show_pdf_list(self.current_folder)).pack(pady=5)

        frame = tk.Frame(self)
        frame.pack()

        canvas = tk.Canvas(frame, width=600, height=500)
        canvas.pack()

        self.render_pdf(canvas)

        control_frame = tk.Frame(self)
        control_frame.pack(pady=5)

        tk.Button(control_frame, text="上一页", command=lambda: self.change_page(-1)).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="下一页", command=lambda: self.change_page(1)).pack(side=tk.LEFT, padx=5)

        if self.audio_path:
            tk.Button(control_frame, text="播放", command=self.play_audio).pack(side=tk.LEFT, padx=5)
            tk.Button(control_frame, text="暂停", command=self.pause_audio).pack(side=tk.LEFT, padx=5)
            tk.Button(control_frame, text="停止", command=self.stop_audio).pack(side=tk.LEFT, padx=5)

    # 渲染PDF页面
    def render_pdf(self, canvas):
        page = self.pdf_document[self.current_page]
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img = img.resize((600, 500), Image.LANCZOS)

        self.tk_img = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)

    # 翻页
    def change_page(self, delta):
        if not self.pdf_document:
            return
        new_page = self.current_page + delta
        if 0 <= new_page < len(self.pdf_document):
            self.current_page = new_page
            self.show_pdf_page()

    # 播放音频
    def play_audio(self):
        if self.audio_path:
            pygame.mixer.init()
            pygame.mixer.music.load(self.audio_path)
            pygame.mixer.music.play()

    # 暂停音频
    def pause_audio(self):
        pygame.mixer.music.pause()

    # 停止音频
    def stop_audio(self):
        pygame.mixer.music.stop()

    # 清空屏幕
    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

# 运行应用
if __name__ == "__main__":
    app = PDFPlayerApp()
    app.mainloop()
