"""
GUI app that takes a .json, opens with an integrated matplotlib, and displays an
isometric render of that object in the .json
"""
import json
import itertools
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter.ttk import Notebook

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as pyplot
from mpl_toolkits.mplot3d import axes3d
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

sizes = [15*8]
colors = ['white', 'red', 'green', 'blue', 'purple', 'orange', 'yellow', 'pink']

""" 
Assuming start orientation is 
        +y  
            
-x    (0, 0, 0)    +x
            
        -y  
"""
def x_axis_rotation(vertices, angle):
    """ 
    vertices: 2D np.array([[x_i, y_i, z_i], [x_2, y_2, z_2] ... [x_f, y_f, z_f]])
    
    angle: an angle in degrees to rotate the vertices by.
    """
    theta = np.deg2rad(angle)
    rot_x = np.array([[1, 0, 0],
                      [0, np.cos(theta), -np.sin(theta)],
                      [0, np.sin(theta), np.cos(theta)]])
    return [np.matmul(rot_x, v) for v in vertices]

def y_axis_rotation(vertices, angle):
    theta = np.deg2rad(angle)
    rot_y = np.array([[np.cos(theta), 0, -np.sin(theta)],
                      [0, 1, 0],
                      [np.sin(theta), 0, np.cos(theta)]])
    return [np.matmul(rot_y, v) for v in vertices]

def z_axis_rotation(vertices, angle):
    theta = np.deg2rad(angle)
    rot_z = np.array([[np.cos(theta), -np.sin(theta), 0],
                      [np.sin(theta), np.cos(theta), 0],
                      [0, 0, 1]])
    return [np.matmul(rot_z, v) for v in vertices]


class IsometricRenderer:
    def __init__(self, root):
        self.root = root
        self.root.title('Isometric Render Tool')
        paddings = {'padx': 5, 'pady': 5}
        style = ttk.Style()
        style.theme_use('clam')
        
        
        pyplot.style.use('dark_background')
        self.fig, self.ax = pyplot.subplots()
        self.fig.set_figheight(3)
        self.fig.set_figwidth(3)
        self.ax.grid(True, 'both')
        self.ax.axhline(y=0, color='red')
        self.ax.axvline(x=0, color='red')
        self.ax.set_xbound(-1, 1)
        self.ax.set_ybound(-1, 1)

        # self.ax.set_axis_off()
        self.ax.set_aspect('equal')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.widget = self.canvas.get_tk_widget()
        self.widget.grid(row=0, rowspan=4, column=0, columnspan=4)
        
        
        self.shape_choice = tk.StringVar()
        shape_options = ['Tetrahedron', 'Hexahedron', 'Octahedron', 'Triangle', 'Square']
        self.shape_menu = ttk.OptionMenu(self.root, self.shape_choice, shape_options[0], *shape_options, 
                                         command=self.load_shape)
        self.shape_menu.grid(row=0, column=4, columnspan=2, sticky='NEW', **paddings)
        
        
        render_button = ttk.Button(self.root, text='Render', command=self.render)
        render_button.grid(row=0, column=6, sticky='NEW', **paddings)
        
        x_label_frame = ttk.LabelFrame(self.root, text='X', labelanchor='n')
        x_label_frame.grid(row=1, rowspan=3, column=4, sticky='NS', **paddings)
        x_label_frame.grid_columnconfigure(0, minsize=100)
        self.x_degrees_entry = tk.StringVar()
        x_label = ttk.Label(x_label_frame, anchor='n', justify='center', textvariable=self.x_degrees_entry)
        x_label.grid(row=0, column=0, sticky='SEW', **paddings)
        self.x_degrees = tk.DoubleVar()
        x_slider = ttk.Scale(x_label_frame, variable=self.x_degrees, length=450,
                             from_=1, to=-1, orient='vertical',
                             command=self.x_rotate)
        x_slider.grid(row=1, rowspan=2, column=0, sticky='NS', **paddings)
        self.x_rotate()
        
        y_label_frame = ttk.LabelFrame(self.root, text='Y', labelanchor='n')
        y_label_frame.grid(row=1, rowspan=3, column=5, sticky='NS', **paddings)
        y_label_frame.grid_columnconfigure(0, minsize=100)
        self.y_degrees_entry = tk.StringVar()
        y_label = ttk.Label(y_label_frame, anchor='n', justify='center', textvariable=self.y_degrees_entry)
        y_label.grid(row=0, column=0, sticky='EW', **paddings)
        self.y_degrees = tk.DoubleVar()
        y_slider = ttk.Scale(y_label_frame, variable=self.y_degrees, length=450,
                             from_=1, to=-1, orient='vertical',
                             command=self.y_rotate)
        y_slider.grid(row=1, rowspan=2, column=0, sticky='NS', **paddings)
        self.y_rotate()
        
        z_label_frame = ttk.LabelFrame(self.root, text='Z', labelanchor='n')
        z_label_frame.grid(row=1, rowspan=3, column=6, sticky='NS', **paddings)
        z_label_frame.grid_columnconfigure(0, minsize=100)
        self.z_degrees_entry = tk.StringVar()
        z_label = ttk.Label(z_label_frame, anchor='n', justify='center', textvariable=self.z_degrees_entry)
        z_label.grid(row=0, column=0, sticky='SEW', **paddings)
        self.z_degrees = tk.DoubleVar()
        z_slider = ttk.Scale(z_label_frame, variable=self.z_degrees, length=450,
                             from_=1, to=-1, orient='vertical',
                             command=self.z_rotate)
        z_slider.grid(row=1, rowspan=2, column=0, sticky='NS', **paddings)
        self.z_rotate()
        
        
        self.shape_file = 'shapes.json'
        self.shape_pts = {}
        self.render_shape = np.array([[]])
        self.load_shapes()
    
    def x_rotate(self, *args):
        degrees = self.x_degrees.get() * 360.0
        self.x_degrees_entry.set(f'{degrees:.2f}')
        # self.render_shape = x_axis_rotation(self.render_shape, degrees)
    
    def y_rotate(self, *args):
        degrees = self.y_degrees.get() * 360.0
        self.y_degrees_entry.set(f'{degrees:.2f}')
        # self.render_shape = y_axis_rotation(self.render_shape, degrees)
    
    def z_rotate(self, *args):
        degrees = self.z_degrees.get() * 360.0
        self.z_degrees_entry.set(f'{degrees:.2f}')
        # self.render_shape = z_axis_rotation(self.render_shape, degrees)
    
    def render(self, *args):
        self.ax.clear()
        # self.ax.set_axis_off()
        self.ax.set_aspect('equal')
        self.ax.grid(True, 'both')
        self.ax.axhline(y=0, color='red')
        self.ax.axvline(x=0, color='red')
        self.ax.set_ybound(-1, 1)
        
        self.render_shape = self.shape_pts[self.shape_choice.get()]
        x = [pt[0] for pt in self.render_shape]
        y = [pt[1] for pt in self.render_shape]
        z = [pt[2] for pt in self.render_shape]
        
        self.ax.plot(x, y)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.widget = self.canvas.get_tk_widget()
        self.widget.grid(row=0, rowspan=4, column=0, columnspan=4)
        self.canvas.draw()
        print(self.canvas.get_width_height())
    
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
    