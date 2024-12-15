import tkinter as tk


class ReusableButton(tk.Button):
    def __init__(self, parent, text, command, **kwargs):
        super().__init__(parent, text=text, command=command, **kwargs)
        self.pack(pady=10)
