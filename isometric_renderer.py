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

def isometric(vertex):
    vertex = z_axis_rotation(vertex, 45)
    vertex = x_axis_rotation(vertex, 26.56)
    return vertex


class IsometricRenderer:
    def __init__(self, root):
        self.root = root
        root.title('Isometric Render Tool')
        paddings = {'padx': 5, 'pady': 5}
        
        
        pyplot.style.use('dark_background')
        self.fig, self.ax = pyplot.subplots()
        self.fig.set_figheight(3)
        self.fig.set_figwidth(3)
        self.ax.set_axis_off()
        self.ax.set_aspect('equal')
        self.plot_canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.widget = self.plot_canvas.get_tk_widget()
        self.widget.grid(row=0, rowspan=4, column=0, columnspan=4)
        
        
        self.shape_choice = tk.StringVar()
        shape_options = ['Tetrahedron', 'Hexahedron', 'Octahedron', 'Triangle', 'Square']
        self.shape_menu = ttk.OptionMenu(self.root, self.shape_choice, shape_options[0], *shape_options, 
                                         command=self.load_shape)
        self.shape_menu.grid(row=0, column=4, columnspan=2, sticky='NEW', **paddings)
        
        render_button = ttk.Button(self.root, text='Render', command=self.render)
        render_button.grid(row=0, column=6, sticky='NEW', **paddings)
        
        #----------------------------------------------------------------------------------------------------
        # self.x = 0.0
        self.x_entry = tk.DoubleVar(value=0.0)
        # self.x_entry.trace_add(['write'], self.on_x_change)
        x_entry_box = ttk.Entry(master=self.root, justify='center', textvariable=self.x_entry)
        x_entry_box.grid(row=3, column=4, sticky='SEW', **paddings)
        x_entry_box.bind('<Return>', self.on_x_change)
        
        self.y_entry = tk.DoubleVar(value=0.0, name='y_entry')
        # self.y_entry.trace_add(['write'], self.on_y_change)
        y_entry_box = ttk.Entry(master=self.root, justify='center', textvariable=self.y_entry)
        y_entry_box.grid(row=3, column=5, sticky='SEW', **paddings)
        y_entry_box.bind('<Return>', self.on_y_change)
        
        self.z_entry = tk.DoubleVar(value=0.0)
        self.z_entry.trace_add(['write'], self.on_z_change)
        z_entry_box = ttk.Entry(master=self.root, justify='center', textvariable=self.z_entry)
        z_entry_box.grid(row=3, column=6, sticky='SEW', **paddings)
        z_entry_box.bind('<Return>', self.on_z_change)
        
        self.shape_file = 'shapes.json'
        self.shape_pts = {}
        self.load_shapes()
        self.render_shape = self.shape_pts[self.shape_choice.get()]
        self.load_tree_view()
        
    def on_x_change(self, *args):
        
        # assert isinstance(self.render_shape, tk.DoubleVar)
        degrees = self.x_entry.get()
        self.render_shape = x_axis_rotation(self.render_shape, self.x_entry.get())
    
    def on_y_change(self, *args):
        print(f'on_y_change({args})')
        self.render_shape = y_axis_rotation(self.render_shape, self.y_entry.get())
    
    def on_z_change(self, *args):
        print(f'on_z_change({args})')
        self.render_shape = z_axis_rotation(self.render_shape, self.z_entry.get())
        
    def render(self, *args):
        print(f'render({args})')
        self.ax.clear()
        self.ax.set_axis_off()
        self.ax.set_aspect('equal')
        
        assert len(self.render_shape) >= 3
        self.load_tree_view()
        
        x = [pt[0] for pt in self.render_shape]
        y = [pt[1] for pt in self.render_shape]
        z = [pt[2] for pt in self.render_shape]
        s = sizes[:len(self.render_shape)]
        c = colors[:len(self.render_shape)]
        
        self.ax.scatter(x, y, s, c)
        
        self.plot_canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.widget = self.plot_canvas.get_tk_widget()
        self.widget.grid(row=0, rowspan=4, column=0, columnspan=4)
        self.plot_canvas.draw()
        
    
    def get_filename(self, full_path):
        i = full_path.rfind('/') + 1
        return full_path[i:]
    
    def load_shapes(self):
        with open(self.shape_file, 'r') as f:
            self.shape_pts = json.load(f)
    
    def load_shape(self, *args):
        print(f'load_shape({args})')
        self.render_shape = self.shape_pts[self.shape_choice.get()]
        self.x_entry.set(0)
        self.y_entry.set(0)
        self.z_entry.set(0)

    def load_tree_view(self, *args):
        print(f'load_tree_view({args})')
        tree = ttk.Treeview(self.root, columns=('x', 'y', 'z'), show='headings')
        tree.heading('x', text='X')
        tree.heading('y', text='Y')
        tree.heading('z', text='Z')
        tree.column('x', stretch=True, anchor='center')
        tree.column('y', stretch=True, anchor='center')
        tree.column('z', stretch=True, anchor='center')
        for pt in self.render_shape:
            item = tree.insert('', 'end')
            tree.set(item, 'x', f'{pt[0]:.2f}')
            tree.set(item, 'y', f'{pt[1]:.2f}')
            tree.set(item, 'z', f'{pt[2]:.2f}')
        tree.grid(row=4, rowspan=1, column=4, columnspan=3, sticky='NSEW')
        
    
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
    