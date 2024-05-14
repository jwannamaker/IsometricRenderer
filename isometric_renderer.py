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

# tetrahedron_x = [ np.sqrt(8/9), -np.sqrt(2/9), -np.sqrt(2/9), 0 ]
# tetrahedron_y = [ 0           , np.sqrt(2/3) , -np.sqrt(2/3), 0 ]
# tetrahedron_z = [ -1/3        , -1/3         , -1/3         , 1 ]


# This is the format that I want vertex data to be in once loaded from .json
tetrahedron_pts = np.array([[np.sqrt(8/9), 0, -1/3],
                            [-np.sqrt(2/9), np.sqrt(2/3), -1/3],
                            [-np.sqrt(2/9), -np.sqrt(2/3), -1/3],
                            [0, 0, 1]])


flat_square_pts = np.array([[0, 1, 1],
                            [0, 0, 1],
                            [1, 0, 1],
                            [1, 1, 1]])

def isometric(vertex):
    """ 
    Input: 1D np.array 
    1. Rotation about the z-axis by 45˚ (ccw)
    2. Rotation about the x-axis by 26.565˚ (ccw) -> backwards tilt
    
    Assuming start orientation is 
            +y  
                
    -x    (0, 0, 0)    +x
                
            -y  
    """
    vertex = z_axis_rotation(vertex, 45)
    vertex = x_axis_rotation(vertex, 26.56)
    return vertex

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


# def edges(vertices):
#     return list(itertools.pairwise(vertices))

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
        self.shape = tetrahedron_pts
        self.edges = []
        
        self.shape_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='Shape', menu=self.shape_menu)
        self.shape_menu.add_cascade(label='Permute', command=self.permute)
        self.shape_menu.add_separator()
        self.shape_menu.add_command(label='Render', command=self.render)
        self.shape_menu.add_command(label='Load', command=self.load_shape)
        self.shape_menu.add_command(label='Save', command=self.save_shape)
        
        pyplot.style.use('dark_background')
        self.fig, self.ax = pyplot.subplots(subplot_kw={'projection': '3d'})
        self.fig.set_figheight(2.56)
        self.fig.set_figwidth(2.56)
        self.ax.set_axis_off()
        self.ax.set_aspect('equal')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.widget = self.canvas.get_tk_widget()
        self.widget.grid(row=2, column=0, columnspan=3)
        
        render_button = ttk.Button(self.root, text='Render', command=self.render)
        render_button.grid(row=0, column=0, sticky='EW', padx=25)
        
        self.isometric_check = tk.BooleanVar()
        isometric_button = ttk.Checkbutton(self.root, text='Isometric', variable=self.isometric_check,
                                           onvalue=True, offvalue=False)
        isometric_button.grid(row=1, column=0, sticky='EW', padx=25)
        
        self.fill_check = tk.BooleanVar()
        fill_button = ttk.Checkbutton(self.root, text='Fill', variable=self.fill_check,
                                      onvalue=True, offvalue=False)
        fill_button.grid(row=1, column=1, sticky='EW', padx=25)
        
        permute_button = ttk.Button(self.root, text='Permute', command=self.permute)
        permute_button.grid(row=0, column=2, sticky='EW', padx=25)
    
    def render(self):
        self.ax.clear()
        self.ax.set_axis_off()
        self.ax.set_aspect('equal')
        
        x, y = [i[0] for i in self.shape], [i[1] for i in self.shape]
        iso_points = [isometric(v) for v in self.shape]
        
        if self.isometric_check.get():
            self.ax.scatter(iso_points[0], iso_points[1])
            self.ax.plot(iso_points[0], iso_points[1])
            if self.fill_check.get():
                self.ax.fill(iso_points[0], iso_points[1])
        else:
            self.ax.scatter(x, y)
            self.ax.plot(x, y)
        
            if self.fill_check.get():
                self.ax.fill(x, y)
            
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.widget = self.canvas.get_tk_widget()
        self.widget.grid(row=2, column=0, columnspan=3)
        self.canvas.draw()
        
    def permute(self):
        # self.shape = tetrahedron_pts
        
        self.ax.clear()
        self.ax.set_axis_off()
        self.ax.set_aspect('equal')
        
        edges = list(itertools.permutations(tetrahedron_pts, 3))
        for edge in edges:
            print(edge)
            print()
        
        # x, y, _ = [[e[i] for i in e] for e in edges]
        
        for edge in edges:
            for pt in edge:
                self.ax.scatter(pt[0], pt[1])
                self.ax.plot(pt[0], pt[1])
            
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.widget = self.canvas.get_tk_widget()
        self.widget.grid(row=2, column=0, columnspan=3)
        self.canvas.draw()
        
    
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
        # self.shape_file = filedialog.askopenfilename(parent=self.root)
        self.shape = tetrahedron_pts
        for i, v in enumerate(self.shape):
            print(f'Point {i}: [{v[0]}, {v[1]}, {v[2]}]')
    
    def save_shape(self):
        filedialog.asksaveasfile(parent=self.root, initialfile=self.get_filename(self.shape_file))
    
if __name__ == '__main__':
    root = tk.Tk()
    app = IsometricRenderer(root)
    root.mainloop()    
    
    