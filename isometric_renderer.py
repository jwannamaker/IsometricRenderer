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
        self.widget.grid(row=2, column=0, columnspan=4)
        
        self.shape_choice = tk.StringVar()
        shape_options = ['Tetrahedron', 'Hexahedron', 'Octahedron', 'Triangle', 'Square']
        self.shape_menu = ttk.OptionMenu(self.root, self.shape_choice, shape_options[0], *shape_options, 
                                         command=self.load_shape)
        self.shape_menu.grid(row=0, column=0, columnspan=2, sticky='EW', **paddings)
        
        self.display_choice = tk.StringVar()
        display_options = ['2D', 'Isometric', '3D']
        self.display_menu = ttk.OptionMenu(self.root, self.display_choice, display_options[0], *display_options, 
                                           command=self.render)
        self.display_menu.grid(row=0, column=2, columnspan=2, sticky='EW', **paddings)
        
        render_button = ttk.Button(self.root, text='Render', command=self.render)
        render_button.grid(row=0, column=4, sticky='E', **paddings)
        
        
        slider_frame = ttk.Frame(self.root)
        slider_frame.grid(row=2, column=4, sticky='NS', **paddings)
        
        self.x_degrees = tk.DoubleVar()
        x_slider = ttk.Scale(slider_frame, variable=self.x_degrees, 
                             length=450,
                             from_=-1, to=1, orient='vertical',
                             command=self.rotate)
        x_slider.grid(row=0, column=0, sticky='NS', **paddings)
            
        self.y_degrees = tk.DoubleVar()
        y_slider = ttk.Scale(slider_frame, variable=self.y_degrees, 
                             length=450,
                             from_=-1, to=1, orient='vertical',
                             command=self.rotate)
        y_slider.grid(row=0, column=1, sticky='NS', **paddings)
        
        self.z_degrees = tk.DoubleVar()
        z_slider = ttk.Scale(slider_frame, variable=self.z_degrees, 
                             length=450,
                             from_=-1, to=1, orient='vertical',
                             command=self.rotate)
        z_slider.grid(row=0, column=2, sticky='NS', **paddings)
        
        self.shape_file = 'shapes.json'
        self.shape_pts = {}
        self.render_shape = np.array([[]])
        self.load_shapes()
    
    def rotate(self, *args):
        # Normalize 
        
        # Apply x rotation
        self.render_shape = x_axis_rotation()
        
        # Apply y rotation
        
        
        # Apply z rotation
        
        
        self.render()
    
    def render(self, *args):
        self.ax.clear()
        self.ax.set_axis_off()
        self.ax.set_aspect('equal')
        
        self.render_shape = self.shape_pts[self.shape_choice.get()]
        x = [pt[0] for pt in self.render_shape]
        y = [pt[1] for pt in self.render_shape]
        z = [pt[2] for pt in self.render_shape]
        
        if self.display_choice.get() == '2D':
            self.ax.plot(x, y)
        elif self.display_choice.get() == 'Isometric':
            self.ax.plot(x, y)
        elif self.display_choice.get() == '3D':
            self.ax.plot(x, y, z)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.widget = self.canvas.get_tk_widget()
        self.widget.grid(row=2, column=0, columnspan=4)
        self.canvas.draw()
    
    def get_filename(self, full_path):
        i = full_path.rfind('/') + 1
        return full_path[i:]
    
    def load_shapes(self):
        with open(self.shape_file, 'r') as f:
            self.shape_pts = json.load(f)
    
    def load_shape(self, *args):
        with open(self.shape_file, 'r') as f:
            file_dict = json.load(f)
            if len(args) and args[0] in list(file_dict.keys()):
                self.shape_pts[args[0]] = file_dict[args[0]]
    
    def save_shapes(self):
        save_file = filedialog.asksaveasfile(parent=self.root)
        with open(save_file, 'w') as f:
            json.dump({self.shape_choice.get(): self.shape_pts}, f, indent=4)
    
    def save_shape(self, *args):
        save_file = filedialog.asksaveasfile(parent=self.root)
        with open(save_file, 'w') as f:
            json.dump({self.shape_choice.get(): self.shape_pts}, f, indent=4)
    
    
if __name__ == '__main__':
    root = tk.Tk()
    app = IsometricRenderer(root)
    root.mainloop()    
    