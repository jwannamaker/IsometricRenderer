"""
GUI app that takes a .json, opens with an integrated matplotlib, and displays an
isometric render of that object in the .json
"""
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import json
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class IsometricRenderer:
    def __init__(self, root):
        self.root = root
        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.grid()
        root.title('Isometric Render')
        
        permute_button = ttk.Button(self.root, text='Permute', command=self.permute).grid(row=1, column=1)
        # permute_button.pack(padx=10, pady=10)

        render_button = ttk.Button(self.root, text='Render', command=self.render).grid(row=2, column=1)
        # render_button.pack(padx=10, pady=10)
        
        load_button = ttk.Button(self.root, text='Load JSON', command=self.load_json).grid(row=3, column=1)        
        # load_button.pack(padx=10, pady=10)
        
        save_button = ttk.Button(self.root, text='Save JSON', command=self.save_json).grid(row=4, column=1)
        # save_button.pack(padx=10, pady=10)
        
        export_button = ttk.Button(self.root, text='Export PNG', command=self.export).grid(row=5, column=1)
        # export_button.pack(padx=10, pady=10)
        
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots()
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.widget = self.canvas.get_tk_widget().grid(row=0, column=0)
        # self.widget.pack(padx=10, pady=10)
        
    def permute(self):
        pass
    
    def render(self):
        pass
    
    def load_json(self):
        pass
    
    def save_json(self):
        pass
    
    def export(self):
        pass
    
if __name__ == '__main__':
    root = tk.Tk()
    app = IsometricRenderer(root)
    root.mainloop()    
    