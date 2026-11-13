"""Standalone Grad-CAM visualiser.

Usage (from the repo root):
    python -m ml.gradcam path/to/leaf.jpg
"""
import os
import sys

import cv2
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model

from ml.predict import BASE_DIR, IMG_SIZE, get_class_names, model, predict_disease, preprocess
from ml.severity_detection import detect_severity

LAST_CONV_LAYER = "Conv_1"

IMAGE_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    BASE_DIR, "data", "dataset", "test", "Pepper__bell___Bacterial_spot",
    "0a4c007d-41ab-4659-99cb-8a4ae4d07a55___NREC_B.Spot 1954.JPG",
)

class_names = get_class_names()

img_rgb, img_array = preprocess(IMAGE_PATH)

pred_class_index, confidence = predict_disease(IMAGE_PATH)
predicted_label = class_names[pred_class_index].replace("__", " ").replace("_", " ")

print("Predicted Disease:", predicted_label)
print(f"Confidence: {confidence:.2f}%")

grad_model = Model(
    inputs=model.input,
    outputs=[model.get_layer(LAST_CONV_LAYER).output, model.output]
)

with tf.GradientTape() as tape:
    conv_outputs, predictions = grad_model(img_array)
    loss = predictions[:, pred_class_index]

grads = tape.gradient(loss, conv_outputs)
pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

heatmap = conv_outputs[0] @ pooled_grads[..., tf.newaxis]
heatmap = np.maximum(tf.squeeze(heatmap).numpy(), 0)
if np.max(heatmap) > 0:  # avoid divide-by-zero on an all-zero map
    heatmap /= np.max(heatmap)

severity_level, severity_percent = detect_severity(heatmap)

print("Severity Level:", severity_level)
print(f"Infected Area: {severity_percent:.2f}%")

heatmap = cv2.resize(heatmap, (IMG_SIZE, IMG_SIZE))
heatmap_color = cv2.cvtColor(
    cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET), cv2.COLOR_BGR2RGB
)
overlay = cv2.addWeighted(img_rgb, 0.75, heatmap_color, 0.25, 0)

plt.figure(figsize=(8, 4))

plt.subplot(1, 2, 1)
plt.title("Original Leaf")
plt.imshow(img_rgb)
plt.axis("off")

plt.subplot(1, 2, 2)
plt.title(
    f"GradCAM\nDisease: {predicted_label} | Confidence: {confidence:.2f}%"
    f"\nSeverity: {severity_level} ({severity_percent:.2f}%)"
)
plt.imshow(overlay)
plt.axis("off")

plt.show()
