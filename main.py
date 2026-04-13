import tkinter as tk
from tkinter import ttk
from ui import App

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam')
    
    app = App(root)
    root.mainloop()