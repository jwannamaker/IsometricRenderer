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
        self.root.bind('<Return>', self.render, add=True)
        
        
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
        self.x_degrees = tk.DoubleVar(value=0.0)
        self.x_degrees.trace_add(['write'], self.on_x_change)
        
        self.x_entry = tk.DoubleVar(value=0.0)
        x_label = ttk.Entry(self.root, justify='center', textvariable=self.x_entry)
        x_label.grid(row=3, column=4, sticky='SEW', **paddings)
        
        self.x_slider = tk.Scale(self.root, variable=self.x_degrees, width=15, length=300,
                                  from_=360.0, to=-360.0, orient='vertical', tickinterval=360,
                                  command=self.x_slider_change)
        self.x_slider.grid(row=1, column=4, sticky='NS', **paddings)
        self.x_slider.bind('<KeyPress>', self.x_slider_change, add=True)
        self.x_slider.bind('<KeyRelease>', self.x_slider_change, add=True)
        #----------------------------------------------------------------------------------------------------
        self.y_entry = tk.DoubleVar(value=0.0)
        y_label = ttk.Entry(self.root, justify='center', textvariable=self.y_entry)
        y_label.grid(row=3, column=5, sticky='SEW', **paddings)
        # y_label.bindtags(['angle_change', 'entry', 'y'])
        
        self.y_degrees = tk.DoubleVar()
        self.y_slider = tk.Scale(self.root, variable=self.y_degrees, width=15, length=300,
                                  from_=360.0, to=-360.0, orient='vertical', tickinterval=360,
                                  command=self.y_slider_change)
        self.y_slider.grid(row=1, column=5, sticky='NS', **paddings)
        # self.y_slider.bindtags(['angle_change', 'slider', 'y'])
        #----------------------------------------------------------------------------------------------------
        self.z_entry = tk.DoubleVar(value=0.0)
        z_label = ttk.Entry(self.root, justify='center', textvariable=self.z_entry)
        z_label.grid(row=3, column=6, sticky='SEW', **paddings)
        # z_label.bindtags(['angle_change', 'entry', 'z'])
        
        self.z_degrees = tk.DoubleVar()
        self.z_slider = tk.Scale(self.root, variable=self.z_degrees, width=15, length=300,
                                  from_=360.0, to=-360.0, orient='vertical', tickinterval=360,
                                  command=self.z_slider_change)
        self.z_slider.grid(row=1, column=6, sticky='NS', **paddings)
        
        # self.z_slider.bindtags(['angle_change', 'slider', 'z'])
        #----------------------------------------------------------------------------------------------------
        
        self.shape_file = 'shapes.json'
        self.shape_pts = {}
        self.load_shapes()
        self.render_shape = self.shape_pts[self.shape_choice.get()]
        self.load_tree_view()
        
    def on_x_change(self, *args):
        print(f'on_x_change: {args}')    
        self.render_shape = x_axis_rotation(self.render_shape, self.x_degrees.get())
    
    def x_slider_change(self, *args):
        print(f'x slider changed to {args[0]}')
        self.x_degrees.set(args[0])
    
    def x_entry_change(self, *args):
        self.x_slider.set(self.x_entry.get())
        self.x_degrees.set(self.x_entry.get())
        self.render_shape = x_axis_rotation(self.render_shape, self.x_degrees.get())
    
    def y_slider_change(self, *args):
        self.y_entry.set(self.y_slider.get())
        self.x_degrees.set(self.y_slider.get())
        self.render_shape = y_axis_rotation(self.render_shape, self.y_degrees.get())
    
    def y_entry_change(self, *args):
        self.y_slider.set(self.y_entry.get())
        self.x_degrees.set(self.y_entry.get())
        self.render_shape = y_axis_rotation(self.render_shape, self.y_degrees.get())
    
    def z_slider_change(self, *args):
        self.z_entry.set(self.z_slider.get())
        self.x_degrees.set(self.z_slider.get())
        self.render_shape = z_axis_rotation(self.render_shape, self.z_degrees.get())
    
    def z_entry_change(self, *args):
        self.z_slider.set(self.z_entry.get())
        self.x_degrees.set(self.z_entry.get())
        self.render_shape = z_axis_rotation(self.render_shape, self.z_degrees.get())
        
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
        self.x_slider.set(0)
        self.y_slider.set(0)
        self.z_slider.set(0)

    def load_tree_view(self, *args):
        print(f'load_tree_view({args})')
        tree = ttk.Treeview(self.root, columns=('x', 'y', 'z'), show='headings')
        tree.heading('x', text='X')
        tree.heading('y', text='Y')
        tree.heading('z', text='Z')
        tree.column('x', stretch=True, anchor='center')
        tree.column('y', stretch=True, anchor='center')
        tree.column('z', stretch=True, anchor='center')
        for pt in list(self.shape_pts[self.shape_choice.get()]):
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
    