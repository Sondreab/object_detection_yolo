from task2 import *
from task2_tests import *
import numpy as np


### Testing task 2a-b

test_iou()
test_precision()
test_recall()

### Testing task 2c
"""
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
"""

test_get_all_box_matches()


### Testing task 2d

test_calculate_individual_image_result()

test_calculate_precision_recall_all_images()

test_get_precision_recall_curve()
