from task2 import *
import numpy as np


b1 = np.array([
    [0, 0, 1, 1],
    [0.25, 0.25, 1, 1],
    [0.5, 0.5, 2, 2]
])
b2 = np.array([
    [0.25, 0.25, 1, 1],
    [0, 0, 1, 1]
])

get_all_box_matches(b1, b2, 0)

print("----------------------\n")