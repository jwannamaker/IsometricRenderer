"""
GUI app that takes a .json, opens with an integrated matplotlib, and displays an
isometric render of that object in the .json
"""
import json
import tkinter as tk
from tkinter import ttk
from tkinter import colorchooser
from tkinter import filedialog

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# tetrahedron_x = [ np.sqrt(8/9), -np.sqrt(2/9), -np.sqrt(2/9), 0 ]
# tetrahedron_y = [ 0           , np.sqrt(2/3) , -np.sqrt(2/3), 0 ]
# tetrahedron_z = [ -1/3        , -1/3         , -1/3         , 1 ]


# This is the format that I want vertex data to be in once loaded from .json
tetrahedron_pts = np.array([[np.sprt(8/9), 0, -1/3],
                            [-np.sqrt(2/9), np.sqrt(2/3), -1/3],
                            [-np.sqrt(2/9), -np.sqrt(2/3), -1/3],
                            [0, 0, 1]])

def isometric(x, y, z):
    """ Takes 3D coordinate and returns the same coordinate after 
        1. Rotation about the z-axis by 45˚ (ccw)
        2. Rotation about the x-axis by 26.565˚ (ccw) -> backwards tilt
    
    Assuming start orientation is 
            +y  ^
                |
                |  (0, 0, 0)
                | /
    -x <--------+--------> +x
                |
                |
                |
            -y  
    """
    alpha = np.deg2rad(45)  # First rotation around z-axis.
    beta = np.deg2rad(26.56505118)  # Second rotation around x-axis.
    
    xy_ratio = np.cos(alpha) / np.cos(beta) # Do I even need foreshortening at all??
    z_ratio = np.sin(alpha) / np.sin(beta)
    
    rot_1 = np.array([[np.cos(alpha), -np.sin(alpha), 0],
                      [np.sin(alpha), np.cos(alpha), 0],
                      [0, 0, 1]])
    
    rot_2 = np.array([[1, 0, 0],
                      [0, np.cos(beta), -np.sin(beta)],
                      [0, np.sin(beta), np.cos(beta)]])

    result = np.matmul(np.matmul(rot_1, rot_2), np.array([x, y, z]))
    
    return result


def prep_render(vertices):
    """ Orders each vertex by ascending z value
    Input: 2D np.array
    Returns list[x: int], list[y: int], list[z: int]
    """
    # Note: sort() only works for lists, sorted() does everything else except it's In Place
    render_order = vertices.sort(key=lambda v: v[2])  # sort by z value
    x_coords = render_order[:, 0]
    y_coords = render_order[:, 1]
    z_coords = render_order[:, 2]
    return x_coords, y_coords, z_coords


class IsometricRenderer:
    def __init__(self, root):
        self.root = root
        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.grid(padx=20, pady=20)
        root.title('Isometric Render Tool')
        
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        self.color_file = ''
        self.color_a = (255, 255, 255)
        self.color_b = (0, 0, 0)
        
        self.color_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='Color', menu=self.color_menu)
        self.color_menu.add_command(label='Choose Color A', command=self.choose_color_a)
        self.color_menu.add_command(label='Choose Color B', command=self.choose_color_b)
        self.color_menu.add_separator()
        self.color_menu.add_command(label='Render', command=self.render)
        self.color_menu.add_command(label='Load', command=self.load_colors)
        self.color_menu.add_command(label='Save', command=self.save_colors)
        
        self.shape_file = ''
        self.shape = {}
        
        self.shape_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='Shape', menu=self.shape_menu)
        self.shape_menu.add_cascade(label='Permute', command=self.permute)
        self.shape_menu.add_separator()
        self.shape_menu.add_command(label='Render', command=self.render)
        self.shape_menu.add_command(label='Load', command=self.load_shape)
        self.shape_menu.add_command(label='Save', command=self.save_shape)
        
        # plt.style.use('dark_background')
        plt.axis('off')
        # self.color_ax.axes.set_visible(False)
        self.color_fig, self.color_ax = plt.subplots(nrows=2, height_ratios=[1, 7])
        self.color_fig.set_frameon(False)
        
        self.color_canvas = FigureCanvasTkAgg(self.color_fig, master=self.root)
        self.color_widget = self.color_canvas.get_tk_widget()\
            .grid(row=0, column=0)
        
        render_button = ttk.Button(self.root, text='Render', command=self.render)\
            .grid(row=0, column=3, sticky='N')
        
        permute_button = ttk.Button(self.root, text='Permute', command=self.permute)\
            .grid(row=0, column=2, sticky='N')
    
    def render(self):
        if self.color_file == '':
            return
        if self.shape_file == '':
            return
        self.color_fig.clear()
        # some change here.
        
        self.color_canvas.draw()
        
    def permute(self):
        pass
    
    def get_filename(self, full_path):
        i = full_path.rfind('/') + 1
        return full_path[i:]
    
    def choose_color_a(self):
        colorchooser.Chooser(self.root, initialcolor=self.color_a)
        self.color_a = colorchooser.askcolor()
        print(self.color_a)
        
    def choose_color_b(self):
        colorchooser.Chooser(self.root, initialcolor=self.color_b)
        self.color_b = colorchooser.askcolor()
        print(self.color_b)
    
    def load_colors(self):
        self.color_file = filedialog.askopenfilename(parent=self.root)
    
    def save_colors(self):
        filedialog.asksaveasfile(parent=self.root, initialfile=self.get_filename(self.color_file))
        
    def load_shape(self):
        self.shape_file = filedialog.askopenfilename(parent=self.root)
    
    def save_shape(self):
        filedialog.asksaveasfile(parent=self.root, initialfile=self.get_filename(self.shape_file))
    
if __name__ == '__main__':
    root = tk.Tk()
    app = IsometricRenderer(root)
    root.mainloop()    
    
    