from tkinterdnd2 import TkinterDnD
from ui.tkinter_gui import PdfProApp

if __name__ == "__main__":
    # Инициализация корня с поддержкой Drag-and-Drop
    root = TkinterDnD.Tk()
    app = PdfProApp(root)
    root.mainloop()