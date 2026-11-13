import os
import cv2
import numpy as np
from tensorflow.keras.models import load_model

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "models", "best_model.h5")
TRAIN_DIR = os.path.join(BASE_DIR, "data", "dataset", "train")
IMG_SIZE = 224

model = load_model(MODEL_PATH)


def get_class_names(train_dir=TRAIN_DIR):
    # Directories only, sorted - same ordering as flow_from_directory.
    return sorted(
        d for d in os.listdir(train_dir)
        if os.path.isdir(os.path.join(train_dir, d))
    )


def preprocess(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Image not found: {image_path}")
    # The model was trained on RGB images (Keras/PIL); OpenCV loads BGR.
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    return img, np.expand_dims(img / 255.0, axis=0)


def predict_disease(image_path):
    _, img_array = preprocess(image_path)
    predictions = model.predict(img_array, verbose=0)
    pred_class = int(np.argmax(predictions[0]))
    confidence = float(predictions[0][pred_class] * 100)
    return pred_class, confidence


if __name__ == "__main__":
    import sys

    class_names = get_class_names()

    IMAGE_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        BASE_DIR, "data", "dataset", "test", "Pepper__bell___Bacterial_spot",
        "0a4c007d-41ab-4659-99cb-8a4ae4d07a55___NREC_B.Spot 1954.JPG",
    )

    pred_class, confidence = predict_disease(IMAGE_PATH)

    disease = class_names[pred_class].replace("__", " ").replace("_", " ")

    print("Disease:", disease)
    print(f"Confidence: {confidence:.2f}%")
