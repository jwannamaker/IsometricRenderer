"""
GUI app that takes a .json, opens with an integrated matplotlib, and displays an
isometric render of that object in the .json
"""
import json
import itertools
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import Notebook
from tkinter import colorchooser
from tkinter import filedialog
from tkinter import scrolledtext

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as pyplot
from mpl_toolkits.mplot3d import axes3d
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

""" 
Assuming start orientation is 
        +y  
            
-x    (0, 0, 0)    +x
            
        -y  
"""

def x_axis_rotation(vertex, angle_degrees):
    theta = np.deg2rad(angle_degrees)
    rot_x = np.array([[1, 0, 0],
                      [0, np.cos(theta), -np.sin(theta)],
                      [0, np.sin(theta), np.cos(theta)]])
    return np.matmul(rot_x, vertex)

def y_axis_rotation(vertex, angle_degrees):
    theta = np.deg2rad(angle_degrees)
    rot_y = np.array([[np.cos(theta), 0, -np.sin(theta)],
                      [0, 1, 0],
                      [np.sin(theta), 0, np.cos(theta)]])
    return np.matmul(rot_y, vertex)

def z_axis_rotation(vertex, angle_degrees):
    theta = np.deg2rad(angle_degrees)
    rot_z = np.array([[np.cos(theta), -np.sin(theta), 0],
                      [np.sin(theta), np.cos(theta), 0],
                      [0, 0, 1]])
    return np.matmul(rot_z, vertex)

def isometric(vertex):
    vertex = z_axis_rotation(vertex, 45)
    vertex = x_axis_rotation(vertex, 26.56)
    return vertex


class IsometricRenderer:
    def __init__(self, root):
        self.root = root
        root.title('Isometric Render Tool')
        paddings = {'padx': 20, 'pady': 20}
        
        pyplot.style.use('dark_background')
        self.fig, self.ax = pyplot.subplots()
        self.fig.set_figheight(2.56)
        self.fig.set_figwidth(2.56)
        self.ax.set_axis_off()
        self.ax.set_aspect('equal')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.widget = self.canvas.get_tk_widget()
        self.widget.grid(row=2, column=0, columnspan=5)
        
        self.shape_choice = tk.StringVar()
        shape_options = ['Tetrahedron', 'Hexahedron', 'Octahedron', 'Triangle', 'Square']
        self.shape_menu = ttk.OptionMenu(self.root, self.shape_choice, shape_options[0], *shape_options, 
                                         command=self.load_shape)
        self.shape_menu.grid(row=0, column=0, columnspan=2, sticky='EW', **paddings)
        
        
        self.shape_file = 'shapes.json'
        self.shape_pts = {}
        self.load_shape(*shape_options)
        
        
        self.display_choice = tk.StringVar()
        display_options = ['2D', 'Isometric', '3D (in progress)']
        self.display_menu = ttk.OptionMenu(self.root, self.display_choice, display_options[0], *display_options, 
                                           command=self.render)
        self.display_menu.grid(row=0, column=2, columnspan=2, sticky='EW', **paddings)
        
        render_button = ttk.Button(self.root, text='Render', command=self.render)
        render_button.grid(row=0, column=4, sticky='EW', **paddings)
    
    def render(self, *args):
        self.ax.clear()
        self.ax.set_axis_off()
        self.ax.set_aspect('equal')
        
        render_shape = self.shape_pts[self.shape_choice.get()]
        x = [pt[0] for pt in render_shape]
        y = [pt[1] for pt in render_shape]
        z = [pt[2] for pt in render_shape]
        
        self.ax.plot(x, y)
        
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.widget = self.canvas.get_tk_widget()
        self.widget.grid(row=2, column=0, columnspan=5)
        self.canvas.draw()
    
    def permute(self):
        
        self.shape_pts 
        
        self.render()
        
    
    def get_filename(self, full_path):
        i = full_path.rfind('/') + 1
        return full_path[i:]
    
    def load_shape(self, *args):
        with open(self.shape_file) as f:
            self.shape_pts = json.load(f)
    
    def save_shape(self):
        self.shape_file = filedialog.asksaveasfile(parent=self.root, 
                                                   initialfile=self.get_filename(self.shape_file))
        with open(self.shape_file, 'w') as f:
            json.dump({self.shape_choice.get(): self.shape_pts}, f, indent=4)
    
if __name__ == '__main__':
    root = tk.Tk()
    app = IsometricRenderer(root)
    root.mainloop()    
    