# 🌿 CropSense AI — Smart Crop Health Detection System

An end-to-end intelligent agricultural diagnosis platform powered by Deep Learning, Flask, and a modern responsive web interface. This platform allows farmers and agronomists to instantly detect crop diseases across Tomatoes, Peppers, and Potatoes with high accuracy, accompanied by detailed actionable recommendations and explainable AI insights.

---

## ✨ Features

- **AI-Powered Disease Diagnosis**: Leverages a robust fine-tuned MobileNetV2 architecture capable of detecting 15 unique plant health statuses across 3 major crop families (Tomato, Potato, Pepper).
- **Explainable AI (XAI)**: Visualizes model focus using **Grad-CAM**, overlaid as a heatmap on the uploaded original leaf showing precisely which lesions or discolorations drove the AI's prediction.
- **Severity Detection Algorithm**: Calculates proportion of infected regions strictly from the Grad-CAM activation heatmap and classifies diseases into *Mild*, *Moderate*, or *Severe* levels.
- **Expert Recommendations Engine**: Generates real-time custom feedback, including:
  - Immediate corrective actions
  - Recommended biological / chemical treatments
  - Agronomic prevention techniques
  - Optimized fertilizer guidelines based on disease type.
- **Stunning Frontend Application**: Built with Vanilla HTML/CSS/JS, incorporating glassmorphism layouts, subtle animation flows, and dark-mode aesthetic for a premium experience natively served by Flask.
- **Printable PDFs / Reports**: Generates and downloads instantaneous HTML-based status reports encapsulating diagnoses and mitigation steps.

---

## 🏗️ Architecture

- **Frontend**: Lightweight, high-performance HTML5, scoped CSS with CSS-variables for easy theming, JavaScript ES6 (Fetch APIs, DOM manipulation, responsive drag-and-drop file uploaders).
- **Backend API**: Python via Flask routing architecture. Endpoint interfaces accept binary forms, process them into tensors, parse them via TensorFlow, synthesize Grad-CAMs, compute bounding analyses via OpenCV, and deliver structured JSON.
- **Machine Learning Core**: 
  - Base: Keras `MobileNetV2` fine-tuned and verified against the PlantVillage dataset via custom dense layers and callbacks.
  - Interpretability Core: Hooked gradient tape layers (specifically tracking `Conv_1` or custom end-layer embeddings).

---

## 🛠️ Project Folder Structure

```
smart-crop-health/
│
├── frontend/                  # Web App Asset Directory
│   ├── index.html             # Main View Layout
│   ├── app.js                 # UI logic, fetch APIs, interactions 
│   └── styles.css             # Theme, animations, grid structures
│
├── dataset/                   # Core dataset structure (split internally)
│   ├── train/                 
│   └── test/                  
│
├── app.py                     # Main Backend Application Pipeline
├── best_model.h5              # Deployed Checkpointed H5 Weights
├── plant_disease_model.h5     # Deprecated/Secondary H5
├── gradcam.py                 # (Standalone) CLI gradcam test logic
├── severity_detection.py      # (Standalone) CLI severity metric check
├── train.py                   # Model training and tuning pipeline code
├── evaluation.py              # Confusion matrix evaluation and metrics
├── predict.py                 # (Standalone) CLI Image Predictor
├── recomendation.py           # Core text engine routing/formatting
├── requirements.txt           # Verified python environment specs
└── README.md                  # Project Documentation
```

---

## 🚀 Getting Started

To run this application locally, ensure you have Python version >= 3.8.

### 1. Setup Virtual Environment

```bash
python -m venv venv

# For Windows:
.\venv\Scripts\activate

# For Linux/Mac:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Smart Server

```bash
python app.py
```

The terminal will log out:
```
============================================================
  🌿 Smart Crop Health Detection System
  Classes: 15
  http://127.0.0.1:5000
============================================================
```

Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000) in your modern web browser! 

---

## 🧪 Model Details & Evaluation

- **Architecture**: `MobileNetV2` Base (top frozen initially) + Custom Head (Global Average Pooling -> Dense(128, ReLU) -> Dropout(0.3) -> Dense(Softmax)).
- **Input Dimensions**: 224x224x3
- **Optimizer**: Adam (learning_rate=0.0001)
- **Callbacks**: `EarlyStopping`, `ModelCheckpoint`, `ReduceLROnPlateau`

### Supported Classes (15):
**Pepper**: Healthy, Bacterial Spot
**Potato**: Healthy, Early Blight, Late Blight
**Tomato**: Healthy, Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot, Spider Mites, Target Spot, Yellow Leaf Curl, Mosaic Virus.

---
*Created and optimized intelligently for smart agriculture diagnostics.*
