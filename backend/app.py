import os
import cv2
import numpy as np
import tensorflow as tf
import base64
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from tensorflow.keras.models import load_model, Model
from werkzeug.utils import secure_filename
from ultralytics import YOLO

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "frontend"), static_url_path="")
CORS(app)

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

MODEL_PATH_1 = os.path.join(BASE_DIR, "ml", "models", "best_model.h5")
MODEL_PATH_2 = os.path.join(BASE_DIR, "ml", "models", "plant_disease_model.h5")
DATASET_PATH = os.path.join(BASE_DIR, "data", "dataset", "train")
IMG_SIZE = 224
LAST_CONV_LAYER = "Conv_1"

from ml.utils.download_model import download_model_if_not_exists

try:
    download_model_if_not_exists()
except Exception as e:
    print("Failed to download model:", e)

print("Loading ensemble models...")
model = load_model(MODEL_PATH_1)
try:
    model_2 = load_model(MODEL_PATH_2)
except Exception as e:
    print("Secondary model not found. Proceeding with single model.", e)
    model_2 = model

try:
    class_names = sorted(os.listdir(DATASET_PATH))
except FileNotFoundError:
    class_names = [
        "Pepper__bell___Bacterial_spot", "Pepper__bell___healthy",
        "Potato___Early_blight", "Potato___Late_blight", "Potato___healthy",
        "Tomato_Bacterial_spot", "Tomato_Early_blight", "Tomato_Late_blight",
        "Tomato_Leaf_Mold", "Tomato_Septoria_leaf_spot",
        "Tomato_Spider_mites_Two_spotted_spider_mite", "Tomato__Target_Spot",
        "Tomato__Tomato_YellowLeaf__Curl_Virus", "Tomato__Tomato_mosaic_virus", 
        "Tomato_healthy"
    ]
    class_names = sorted(class_names)
print(f"Ensemble Models loaded. Classes ({len(class_names)}): {class_names}")

grad_model = Model(
    inputs=model.input,
    outputs=[model.get_layer(LAST_CONV_LAYER).output, model.output]
)

print("Loading YOLOv8 pest model...")
pest_model = YOLO("yolov8n.pt")
print("YOLOv8 loaded.")

RECOMMENDATIONS = {
    "Pepper__bell___Bacterial_spot": {
        "description": "Bacterial spot caused by Xanthomonas bacteria, appearing as dark, water-soaked lesions on leaves and fruit.",
        "immediate_actions": [
            "Remove and destroy infected plant material immediately",
            "Avoid overhead irrigation to reduce leaf wetness",
            "Apply copper-based bactericides (e.g., Kocide 3000)"
        ],
        "treatments": [
            "Copper hydroxide spray (2-3 applications, 7-10 day intervals)",
            "Mancozeb + copper mixture for enhanced protection",
            "Acibenzolar-S-methyl (Actigard) as a plant activator"
        ],
        "prevention": [
            "Use certified disease-free seeds",
            "Practice crop rotation (3-4 year cycle)",
            "Maintain proper plant spacing for air circulation",
            "Plant resistant varieties (e.g., Aristotle, Revolution)"
        ],
        "fertilizer": "Reduce nitrogen; apply balanced NPK (10-10-10). Add calcium to strengthen cell walls.",
        "urgency": "high"
    },
    "Pepper__bell___healthy": {
        "description": "Your pepper plant is in excellent health! No disease detected.",
        "immediate_actions": [
            "Continue your current care routine",
            "Monitor regularly for early signs of stress",
            "Maintain consistent watering schedule"
        ],
        "treatments": ["No treatment needed at this time"],
        "prevention": [
            "Keep soil moisture consistent (avoid drought stress)",
            "Apply organic mulch to retain moisture",
            "Scout for pests weekly",
            "Maintain adequate phosphorus for root health"
        ],
        "fertilizer": "Apply balanced fertilizer (5-10-10) to support fruiting. Avoid excess nitrogen.",
        "urgency": "none"
    },
    "Potato___Early_blight": {
        "description": "Early blight caused by Alternaria solani fungus - dark concentric-ring lesions on older leaves.",
        "immediate_actions": [
            "Remove lower infected leaves immediately",
            "Apply chlorothalonil or mancozeb fungicide",
            "Improve air circulation around plants"
        ],
        "treatments": [
            "Chlorothalonil (Daconil) - apply every 7-10 days",
            "Mancozeb 75 WP at 2kg/acre",
            "Azoxystrobin (Serenade / Quadris) for systemic control",
            "Copper oxychloride 50 WP as an alternative"
        ],
        "prevention": [
            "Use certified disease-free seed potatoes",
            "Rotate crops (3-year cycle - avoid solanaceous crops)",
            "Hill soil around plants to prevent splash spread",
            "Use drip irrigation instead of overhead sprinklers"
        ],
        "fertilizer": "Ensure adequate potassium (K) - use 60-80 kg K2O/ha. Avoid excess nitrogen.",
        "urgency": "medium"
    },
    "Potato___Late_blight": {
        "description": "Late blight (Phytophthora infestans) - the most devastating potato disease. Water-soaked lesions with white mold on undersides.",
        "immediate_actions": [
            "URGENT: Remove and destroy ALL infected tissue immediately",
            "Apply systemic fungicide within 24 hours",
            "Alert neighboring farms as this spreads rapidly",
            "Stop overhead irrigation immediately"
        ],
        "treatments": [
            "Metalaxyl + mancozeb (Ridomil Gold) - most effective",
            "Dimethomorph (Forum 50 WG) for resistant strains",
            "Cymoxanil + mancozeb (Curzate M8) preventatively",
            "Phosphonates (Fosphite) for curative action"
        ],
        "prevention": [
            "Plant resistant varieties (Sarpo Mira, Defender)",
            "Apply preventative fungicides from early season",
            "Destroy volunteer potato plants",
            "Harvest tubers quickly in favorable weather"
        ],
        "fertilizer": "Focus on phosphorus and potassium to enhance resistance. Ca(NO3)2 for calcium nutrition.",
        "urgency": "critical"
    },
    "Potato___healthy": {
        "description": "Your potato crop is healthy! No disease detected. Great job!",
        "immediate_actions": [
            "Continue scouting every 5-7 days",
            "Maintain preventative spray program",
            "Monitor soil moisture levels"
        ],
        "treatments": ["No treatment needed"],
        "prevention": [
            "Apply preventative copper-based sprays before wet season",
            "Ensure good drainage in the field",
            "Hill up plants at 15-20cm growth stage"
        ],
        "fertilizer": "Apply NPK 12-32-16 at planting. Top-dress with urea at hilling stage.",
        "urgency": "none"
    },
    "Tomato_Bacterial_spot": {
        "description": "Bacterial spot (Xanthomonas vesicatoria) - small, dark spots with yellow halos on leaves and fruit.",
        "immediate_actions": [
            "Remove and bag infected leaves for disposal",
            "Apply copper bactericide immediately",
            "Disinfect gardening tools with 10% bleach solution"
        ],
        "treatments": [
            "Copper hydroxide (Kocide 3000) - 7-day spray intervals",
            "Copper sulfate pentahydrate (0.25%)",
            "Streptomycin sulfate (if legal in your region)",
            "Bacillus subtilis (Serenade) as a biological alternative"
        ],
        "prevention": [
            "Plant resistant varieties (FL 47, Quincy)",
            "Use certified disease-free transplants",
            "Avoid working in fields when plants are wet",
            "Practice 2-3 year crop rotation"
        ],
        "fertilizer": "Balanced NPK with emphasis on calcium (Ca) and boron (B) for cell wall strength.",
        "urgency": "high"
    },
    "Tomato_Early_blight": {
        "description": "Early blight (Alternaria solani) - bulls-eye concentric ring patterns, typically starting on bottom leaves.",
        "immediate_actions": [
            "Remove affected lower leaves",
            "Apply protective fungicide",
            "Stake plants to improve airflow"
        ],
        "treatments": [
            "Chlorothalonil - every 7 days in wet weather",
            "Mancozeb 75 WP (2 kg/acre)",
            "Boscalid + pyraclostrobin (Pristine) for advanced cases",
            "Neem oil (organic option) - every 5-7 days"
        ],
        "prevention": [
            "Mulch around base to minimize soil splash",
            "Water at the base; avoid wetting foliage",
            "Ensure balanced plant nutrition",
            "Remove crop debris at end of season"
        ],
        "fertilizer": "Adequate K and Ca nutrition. Use compost to improve soil organic matter and drainage.",
        "urgency": "medium"
    },
    "Tomato_Late_blight": {
        "description": "Late blight (Phytophthora infestans) - very fast spreading. Greasy water-soaked patches, white mold visible in humid conditions.",
        "immediate_actions": [
            "URGENT: Act within 24 hours",
            "Remove and destroy all visibly infected plants",
            "Apply systemic fungicide immediately",
            "Notify local agricultural extension office"
        ],
        "treatments": [
            "Metalaxyl + Mancozeb (Ridomil MZ) - most effective",
            "Propamocarb (Previcur Energy)",
            "Amisulbrom (Leimay) for resistant strains",
            "Mandipropamid (Revus) as a protective spray"
        ],
        "prevention": [
            "Grow resistant varieties (Mountain Magic, Defiant)",
            "Don't compost infected material - burn or bag it",
            "Monitor disease pressure using local forecasting tools",
            "Avoid late-season planting that coincides with cool, wet periods"
        ],
        "fertilizer": "Increase calcium and potassium; reduce excessive nitrogen. Consider seaweed extracts to boost immunity.",
        "urgency": "critical"
    },
    "Tomato_Leaf_Mold": {
        "description": "Leaf mold (Passalora fulva) - yellow patches on upper leaf surface with olive-green to brown mold on undersides.",
        "immediate_actions": [
            "Increase ventilation in greenhouse/tunnel",
            "Reduce humidity below 85%",
            "Remove and destroy severely infected leaves"
        ],
        "treatments": [
            "Chlorothalonil or copper-based fungicides",
            "Difenoconazole (Score 250 EC)",
            "Azoxystrobin (Amistar) - systemic action",
            "Sulfur dust (organic farms)"
        ],
        "prevention": [
            "Grow resistant varieties (Ty-1 gene)",
            "Ensure 30-inch plant spacing for airflow",
            "Avoid high humidity for extended periods",
            "Use drip irrigation"
        ],
        "fertilizer": "Balanced nutrition with emphasis on potassium. Avoid excessive fertilization.",
        "urgency": "medium"
    },
    "Tomato_Septoria_leaf_spot": {
        "description": "Septoria leaf spot - small circular spots with white/grey centers and dark borders, starting on lower leaves.",
        "immediate_actions": [
            "Remove infected lower leaves (up to 1/3 of plant)",
            "Apply protective fungicide spray",
            "Sanitize all garden tools"
        ],
        "treatments": [
            "Chlorothalonil (Bravo 720) - protective",
            "Mancozeb or copper hydroxide",
            "Boscalid + trifloxystrobin (Flint Plus)",
            "Bacillus amyloliquefaciens (Double Nickel LC) - organic"
        ],
        "prevention": [
            "Stake and prune for good air movement",
            "Never till infected leaves into soil",
            "Apply organic mulch to prevent soil splash",
            "Rotate with non-solanaceous crops for 2+ years"
        ],
        "fertilizer": "Well-balanced fertilizer. Ensures adequate calcium and magnesium levels in soil.",
        "urgency": "medium"
    },
    "Tomato_Spider_mites_Two_spotted_spider_mite": {
        "description": "Two-spotted spider mites (Tetranychus urticae) - tiny pests causing stippling, bronzing, and webbing on leaves.",
        "immediate_actions": [
            "Spray plants with strong jet of water to dislodge mites",
            "Apply miticide or neem oil immediately",
            "Increase ambient humidity (mites hate moisture)"
        ],
        "treatments": [
            "Abamectin (Agrimek) - highly effective",
            "Bifenazate (Floramite) - fast knockdown",
            "Spiromesifen (Oberon 2SC)",
            "Neem oil + insecticidal soap (organic)",
            "Predatory mites: Phytoseiulus persimilis (biological)"
        ],
        "prevention": [
            "Monitor undersides of leaves weekly in hot, dry conditions",
            "Avoid broad-spectrum insecticides that kill natural enemies",
            "Maintain adequate plant moisture",
            "Remove weeds that harbour mites"
        ],
        "fertilizer": "Avoid excess nitrogen, which promotes soft growth preferred by mites. Ensure adequate silicon (Si).",
        "urgency": "high"
    },
    "Tomato__Target_Spot": {
        "description": "Target spot (Corynespora cassiicola) - concentric ring lesions on leaves, stems and fruit under warm, humid conditions.",
        "immediate_actions": [
            "Remove severely affected leaves",
            "Apply fungicide spray program",
            "Improve air circulation"
        ],
        "treatments": [
            "Tebuconazole (Folicur) + chlorothalonil",
            "Boscalid + pyraclostrobin (Pristine)",
            "Azoxystrobin + difenoconazole (Amistar Top)",
            "Propiconazole (Tilt)"
        ],
        "prevention": [
            "Use resistant or tolerant varieties",
            "Avoid dense planting",
            "Stake plants for better airflow",
            "Practice crop rotation"
        ],
        "fertilizer": "Ensure balanced NPK. Good potassium levels improve disease tolerance.",
        "urgency": "medium"
    },
    "Tomato__Tomato_YellowLeaf__Curl_Virus": {
        "description": "Tomato Yellow Leaf Curl Virus (TYLCV) - transmitted by whiteflies. Leaves curl upward, turn yellow; plants stunted.",
        "immediate_actions": [
            "URGENT: Remove and destroy infected plants to stop spread",
            "Apply insecticide to control whitefly vectors immediately",
            "Use yellow sticky traps to monitor whitefly populations"
        ],
        "treatments": [
            "No cure - management focuses on vector control",
            "Imidacloprid (Admire) for whitefly control",
            "Spirotetramat (Movento) - systemic whitefly killer",
            "Pyriproxyfen (Knack) - disrupts whitefly reproduction",
            "Reflective mulches to deter whiteflies"
        ],
        "prevention": [
            "Plant TYLCV-resistant varieties (Hazera, Seminis lines)",
            "Use insect-proof nets (50-mesh) in nurseries",
            "Remove and destroy all crop debris",
            "Plant away from known heavily-infested fields"
        ],
        "fertilizer": "Well-balanced nutrition. Adequate silicon can reduce insect feeding. Avoid excess nitrogen.",
        "urgency": "critical"
    },
    "Tomato__Tomato_mosaic_virus": {
        "description": "Tomato mosaic virus (ToMV) - mosaic patterns of light/dark green, leaf distortion, transmitted mechanically.",
        "immediate_actions": [
            "Remove and bag infected plants immediately",
            "Disinfect all tools with 10% bleach or 70% ethanol",
            "Wash hands thoroughly before and after handling plants",
            "Restrict movement between rows"
        ],
        "treatments": [
            "No chemical cure - prevention and removal are key",
            "Spray milk solution (1:10) on leaves - may inactivate virus",
            "Skim milk powder (100g/L) as protective spray"
        ],
        "prevention": [
            "Use TMV-resistant varieties (Celebrity, Mountain Pride)",
            "Start with certified virus-free seeds/transplants",
            "Control aphids and thrips (secondary vectors)",
            "Don't use tobacco near tomato plants"
        ],
        "fertilizer": "Ensure stress-free nutrition with balanced fertilizer to support plant immunity.",
        "urgency": "critical"
    },
    "Tomato_healthy": {
        "description": "Your tomato plant is perfectly healthy! Keep up the excellent work.",
        "immediate_actions": [
            "Continue current care routine",
            "Scout for pests and disease weekly",
            "Ensure consistent watering and fertilization"
        ],
        "treatments": ["No treatment needed"],
        "prevention": [
            "Apply preventative copper or neem oil spray monthly",
            "Train vines and remove suckers for airflow",
            "Deep water 2-3 times per week",
            "Mulch to maintain soil moisture"
        ],
        "fertilizer": "Switch to high-potassium fertilizer (e.g., 5-10-15) once flowering begins to support fruit set.",
        "urgency": "none"
    }
}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def preprocess_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Could not read image")
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (IMG_SIZE, IMG_SIZE))
    return img_resized, np.expand_dims(img_resized / 255.0, axis=0)


def generate_gradcam(img_array, pred_class_index):
    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array)
        loss = predictions[:, pred_class_index]

    grads = tape.gradient(loss, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    conv_out = conv_outputs[0]

    heatmap = conv_out @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap).numpy()
    heatmap = np.maximum(heatmap, 0)

    if np.max(heatmap) > 0:
        heatmap /= np.max(heatmap)

    return heatmap


def detect_severity(heatmap):
    heatmap_uint8 = np.uint8(255 * heatmap)
    _, thresh = cv2.threshold(heatmap_uint8, 150, 255, cv2.THRESH_BINARY)
    infected_pixels = np.sum(thresh == 255)
    total_pixels = thresh.size
    severity_ratio = infected_pixels / total_pixels
    severity_percent = severity_ratio * 100

    if severity_percent < 20:
        severity_level = "Mild"
        severity_color = "#22c55e"
    elif severity_percent < 50:
        severity_level = "Moderate"
        severity_color = "#f59e0b"
    else:
        severity_level = "Severe"
        severity_color = "#ef4444"

    return severity_level, severity_percent, severity_color


def overlay_gradcam(img_rgb, heatmap):
    heatmap_resized = cv2.resize(heatmap, (IMG_SIZE, IMG_SIZE))
    heatmap_color = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
    heatmap_rgb = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)
    overlay = cv2.addWeighted(img_rgb, 0.65, heatmap_rgb, 0.35, 0)
    return overlay


def image_to_base64(img_array):
    _, buffer = cv2.imencode(".jpg", cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR))
    return base64.b64encode(buffer).decode("utf-8")


def format_class_name(cls):
    return cls.replace("__", " - ").replace("_", " ")


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/classes", methods=["GET"])
def get_classes():
    formatted = [{"id": name, "label": format_class_name(name)} for name in class_names]
    return jsonify({"classes": formatted, "total": len(class_names)})


@app.route("/api/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Use JPG, PNG or WEBP"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        img_rgb, img_array = preprocess_image(filepath)

        # ── YOLO Detection ───────────────────────────
        yolo_results = pest_model(filepath)
        pest_annotated_bgr = yolo_results[0].plot()
        pest_annotated_rgb = cv2.cvtColor(pest_annotated_bgr, cv2.COLOR_BGR2RGB)
        pest_b64 = image_to_base64(pest_annotated_rgb)

        detections = []
        for c, conf in zip(yolo_results[0].boxes.cls, yolo_results[0].boxes.conf):
            detections.append({
                "class": pest_model.names[int(c)],
                "confidence": float(conf * 100)
            })

        # ── Predict (Ensemble) ──────────────────────────────
        preds_1 = model.predict(img_array, verbose=0)
        preds_2 = model_2.predict(img_array, verbose=0)
        predictions = (preds_1 + preds_2) / 2.0
        pred_class_index = int(np.argmax(predictions[0]))
        confidence = float(predictions[0][pred_class_index] * 100)

        # Top-5 predictions
        top5_indices = np.argsort(predictions[0])[::-1][:5]
        top5 = [
            {
                "class": format_class_name(class_names[i]),
                "confidence": float(predictions[0][i] * 100)
            }
            for i in top5_indices
        ]

        predicted_class = class_names[pred_class_index]
        predicted_label = format_class_name(predicted_class)

        # Grad-CAM
        heatmap = generate_gradcam(img_array, pred_class_index)

        # Severity
        severity_level, severity_percent, severity_color = detect_severity(heatmap)

        # Overlay
        overlay_img = overlay_gradcam(img_rgb, heatmap)

        # Encode images
        original_b64 = image_to_base64(img_rgb)
        overlay_b64 = image_to_base64(overlay_img)

        # Recommendation 
        rec = RECOMMENDATIONS.get(
            predicted_class,
            {
                "description": f"Analysis complete for {predicted_label}.",
                "immediate_actions": ["Consult a local agronomist"],
                "treatments": ["Refer to regional guidelines"],
                "prevention": ["Practice good agronomic hygiene"],
                "fertilizer": "Follow standard balanced fertilization program.",
                "urgency": "medium"
            }
        )

        is_healthy = "healthy" in predicted_class.lower()

        result = {
            "success": True,
            "prediction": {
                "class": predicted_class,
                "label": predicted_label,
                "confidence": round(confidence, 2),
                "is_healthy": is_healthy,
                "top5": top5
            },
            "severity": {
                "level": severity_level,
                "percentage": round(severity_percent, 2),
                "color": severity_color
            },
            "images": {
                "original": original_b64,
                "gradcam": overlay_b64,
                "yolo": pest_b64
            },
            "detections": detections,
            "recommendation": rec
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "online",
        "model": "Ensemble Soft-Voting (MobileNetV2)",
        "classes": len(class_names),
        "version": "1.0.0"
    })

# MAIN

if __name__ == "__main__":
    print("=" * 60)
    print("  🌿 Smart Crop Health Detection System")
    print(f"  Classes: {len(class_names)}")
    print("  http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
