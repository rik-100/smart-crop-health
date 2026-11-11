import cv2
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import os

from tensorflow.keras.models import load_model, Model  
from predict import predict_disease
from ml.severity_detection import detect_severity

MODEL_PATH = "best_model.h5"

IMAGE_PATH = r"C:\Users\KIIT0001\Documents\smart-crop-health\dataset\test\Pepper__bell___Bacterial_spot\0a4c007d-41ab-4659-99cb-8a4ae4d07a55___NREC_B.Spot 1954.JPG"

DATASET_PATH = "dataset/train"

IMG_SIZE = 224
LAST_CONV_LAYER = "Conv_1"

class_names = sorted(os.listdir(DATASET_PATH))

model = load_model(MODEL_PATH)
print("Model loaded successfully")

img = cv2.imread(IMAGE_PATH)

if img is None:
    raise ValueError(f"Image not found: {IMAGE_PATH}")

img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
img_array = np.expand_dims(img / 255.0, axis=0)

pred_class_index, confidence = predict_disease(IMAGE_PATH, class_names)

predicted_label = class_names[pred_class_index]

print("Predicted Disease:", predicted_label.replace("__"," ").replace("_"," "))
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

conv_outputs = conv_outputs[0]

heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
heatmap = tf.squeeze(heatmap)

heatmap = np.maximum(heatmap, 0)
heatmap /= np.max(heatmap)

severity_level, severity_percent = detect_severity(heatmap)

print("Severity Level:", severity_level)
print(f"Infected Area: {severity_percent:.2f}%")

heatmap = cv2.resize(heatmap, (IMG_SIZE, IMG_SIZE))

heatmap_color = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)

overlay = cv2.addWeighted(img, 0.75, heatmap_color, 0.25, 0)

plt.figure(figsize=(8,4))

plt.subplot(1,2,1)
plt.title("Original Leaf")
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.axis("off")

plt.subplot(1,2,2)
plt.title(
    f"GradCAM\nDisease: {predicted_label.replace('__',' ').replace('_',' ')}"
    f" | Confidence: {confidence:.2f}%"
    f"\nSeverity: {severity_level} ({severity_percent:.2f}%)"
)

plt.imshow(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB))
plt.axis("off")

plt.show()