import cv2
import numpy as np

def detect_severity(heatmap):

    heatmap_uint8 = np.uint8(255 * heatmap)

    _, thresh = cv2.threshold(heatmap_uint8, 150, 255, cv2.THRESH_BINARY)

    infected_pixels = np.sum(thresh == 255)
    total_pixels = thresh.size

    severity_ratio = infected_pixels / total_pixels
    severity_percent = severity_ratio * 100

    if severity_percent < 20:
        severity_level = "Mild"
    elif severity_percent < 50:
        severity_level = "Moderate"
    else:
        severity_level = "Severe"

    return severity_level, severity_percent