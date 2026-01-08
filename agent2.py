


import json
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import os

# -----------------------------
# Config
# -----------------------------
BASE_PATH = r"C:\Users\karth\OneDrive\Desktop\major_test\crop_model"
MODEL_PATH = os.path.join(BASE_PATH, "agent2_model.h5")
CLASSES_PATH = os.path.join(BASE_PATH, "agent2_classes.json")

_model = None
_class_names = None


def _load_resources(model_path=MODEL_PATH, classes_path=CLASSES_PATH):
    """Lazy-load model and class names."""
    global _model, _class_names
    if _model is None:
        _model = load_model(model_path, compile=False)
    if _class_names is None:
        with open(classes_path, "r") as f:
            _class_names = json.load(f)
    return _model, _class_names


def run_agent2(img_path: str):
    """
    Crop Health Agent
    -----------------
    Input : leaf image path
    Output: dict for Agent-4
    """
    if not img_path or not os.path.exists(img_path):
        raise FileNotFoundError(f"Leaf image not found: {img_path}")

    model, class_names = _load_resources()

    img = image.load_img(img_path, target_size=(224, 224))
    arr = image.img_to_array(img) / 255.0
    arr = np.expand_dims(arr, axis=0)

    probs = model.predict(arr, verbose=0)[0]

    # Map probabilities
    prob_map = {
        class_names[i]: float(probs[i])
        for i in range(len(class_names))
    }

    # ---- Smart decision policy ----
    healthy_prob = prob_map.get("Healthy", 0.0)
    mild_prob = prob_map.get("Diseased_mild", 0.0)
    moderate_prob = prob_map.get("Diseased_moderate", 0.0)

    if healthy_prob >= 0.45:
        label = "Healthy"
        confidence = healthy_prob
    elif mild_prob >= moderate_prob:
        label = "Diseased_mild"
        confidence = mild_prob
    else:
        label = "Diseased_moderate"
        confidence = moderate_prob

    return {
        "health_status": label,
        "confidence": round(confidence, 3),
        "probabilities": {
            "Healthy": round(healthy_prob, 3),
            "Diseased_mild": round(mild_prob, 3),
            "Diseased_moderate": round(moderate_prob, 3),
        }
    }


# -----------------------------
# Local test (safe)
# -----------------------------
if __name__ == "__main__":
    test_image = r"C:\Users\karth\OneDrive\Desktop\test_leaf.jpg"
    out = run_agent2(test_image)
    print("Agent-2 Output:", out)
