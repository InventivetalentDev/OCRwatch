import json
import time
from datetime import datetime

import cv2


# https://stackoverflow.com/a/32929315/6257838
def rotate(image, angle, center=None, scale=1.0):
    (h, w) = image.shape[:2]

    if center is None:
        center = (w / 2, h / 2)

    # Perform the rotation
    M = cv2.getRotationMatrix2D(center, angle, scale)
    rotated = cv2.warpAffine(image, M, (w, h))

    return rotated


def write_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

def tme():
    return datetime.utcnow().strftime('%H:%M:%S.%f')