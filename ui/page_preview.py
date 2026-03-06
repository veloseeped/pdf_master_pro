import fitz  
from PIL import Image, ImageTk
import tkinter as tk
import os
from ui.styles import *
from utils.messages import get_msg


class PreviewEngine:
    """Логика обработки PDF страниц."""
    def __init__(self):
        self.doc = None

    def load_document(self, path):
        if path and os.path.exists(path):
            self.doc = fitz.open(path)
            return len(self.doc)
        self.doc = None
        return 0

    def get_page_image(self, page_num, max_width, max_height):
        """Возвращает масштабированное изображение страницы."""
        if not self.doc: return None
        page = self.doc.load_page(page_num)
        # Используем коэффициент 1.0 для базового качества
        pix = page.get_pixmap(matrix=fitz.Matrix(1.0, 1.0))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # ИСПРАВЛЕНИЕ: Используем thumbnail для вписывания в размеры без обрезки
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        return img


class PagePreviewControl(tk.LabelFrame):
    """Виджет предпросмотра с навигацией."""
    def __init__(self, parent):
        super().__init__(parent, text=get_msg("label_preview"), padx=5, pady=5, width=350)
        self.pack_propagate(False)
        self.engine = PreviewEngine()
        self.current_page = 0
        self.tk_image = None
        self._setup_ui()

    def _setup_ui(self):
        self.preview_label = tk.Label(self, text=get_msg("label_no_file"), bg=COLOR_BACKGROUND, anchor="center")
        self.preview_label.pack(fill="both", expand=True)
        
        nav_frame = tk.Frame(self)
        nav_frame.pack(fill="x", pady=5)
        
        tk.Button(nav_frame, text=get_msg("btn_left"), command=self.prev_page).pack(side="left")
        
        center = tk.Frame(nav_frame)
        center.pack(side="left", expand=True)
        self.ent_page = tk.Entry(center, width=5, justify="center")
        self.ent_page.pack(side="left")
        self.ent_page.bind("<Return>", self._on_entry)
        self.lbl_total = tk.Label(center, text=" / 0")
        self.lbl_total.pack(side="left")
        
        tk.Button(nav_frame, text=get_msg("btn_right"), command=self.next_page).pack(side="right")

    def update_preview(self, path):
        total = self.engine.load_document(path)
        self.current_page = 0
        self.lbl_total.config(text=f" / {total}")
        if total > 0:
            self.show_page()
        else:
            self.preview_label.config(image="", text=get_msg("label_file_not_found") if path else get_msg("label_no_file"))

    def show_page(self):
        self.update_idletasks()
        available_w = max(self.preview_label.winfo_width() - 10, 100)
        available_h = max(self.preview_label.winfo_height() - 10, 100)
        img_data = self.engine.get_page_image(self.current_page, available_w, available_h)
        if img_data:
            self.tk_image = ImageTk.PhotoImage(img_data)
            self.preview_label.config(image=self.tk_image, text="")
            self.ent_page.delete(0, tk.END)
            self.ent_page.insert(0, str(self.current_page + 1))
    
    def on_resize(self, event):
        """Перерисовывает страницу при изменении размера окна пользователем."""
        if self.engine.doc:
            # Используем after_cancel/after, если нужно убрать "мерцание", 
            # но для PDF обычно достаточно прямого вызова
            self.show_page()
    
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_page()

    def next_page(self):
        if self.engine.doc and self.current_page < len(self.engine.doc) - 1:
            self.current_page += 1
            self.show_page()

    def _on_entry(self, event):
        val = self.ent_page.get().strip()
        if val.isdigit() and self.engine.doc:
            idx = int(val) - 1
            if 0 <= idx < len(self.engine.doc):
                self.current_page = idx
        self.show_page()

