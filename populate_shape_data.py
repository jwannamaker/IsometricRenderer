import json

import numpy as np
from numpy import sqrt, sin, cos

# This is the format that I want vertex data to be in once loaded from .json
tetrahedron_pts = np.array([[sqrt(8/9), 0, -1/3],
                            [-sqrt(2/9), sqrt(2/3), -1/3],
                            [-sqrt(2/9), -sqrt(2/3), -1/3],
                            [0, 0, 1]])
# tetrahedron_pts = np.array([[0, 0, 0],
#                             [1, 0, 0],
#                             [-1/2, sqrt(3)/2, 0],
#                             [-1/2, -sqrt(3)/2, 0]])

# (0,±1,0),(±1,0,0),(0,0,±1)
octahedron_pts = np.array([[0, 1, 0],
                           [0, -1, 0],
                           [1, 0, 0],
                           [-1, 0, 0],
                           [0, 0, 1],
                           [0, 0, -1]])

# ​(−1,−1,−1),(−1,−1,1),(−1,1,−1),(−1,1,1),(1,−1,−1),(1,−1,1),(1,1,−1),(1,1,1)​
hexahedron_pts = np.array([[-1, -1, -1],
                           [-1, -1, 1],
                           [-1, 1, -1],
                           [-1, 1, 1],
                           [1, -1, -1],
                           [1, -1, 1],
                           [1, 1, -1],
                           [1, 1, 1]])

# (−1,−1,−1),(−1,1,−1),(1,1,−1),(1,−1,−1)
square_pts = np.array([[-1, -1, -1],
                       [-1, 1, -1],
                       [1, 1, -1],
                       [1, -1, -1]])


triangle_pts = np.array([[sqrt(8/9), 0, -1/3],
                         [-sqrt(2/9), sqrt(2/3), -1/3],
                         [-sqrt(2/9), -sqrt(2/3), -1/3]])
 
 
def convert_to_float(vertex):
    return float(vertex[0]), float(vertex[1]), float(vertex[2])

def serialize(vertices):
    return [convert_to_float(vertex) for vertex in vertices]

shapes = {
    'Tetrahedron': serialize(tetrahedron_pts),
    'Octahedron': serialize(octahedron_pts),
    'Hexahedron': serialize(hexahedron_pts),
    'Square': serialize(square_pts),
    'Triangle': serialize(triangle_pts)
}

if __name__ == '__main__':
    
    
    with open('shapes.json', 'w') as f:
        json.dump(shapes, f, indent=4)