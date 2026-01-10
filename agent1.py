


from ultralytics import YOLO
import cv2
import os
from typing import Optional


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "best.pt")


_model = None

def _get_model(path=MODEL_PATH):
    """Lazy-load and cache YOLO model."""
    global _model
    if _model is None:
        _model = YOLO(path)
    return _model


def run_agent1(
    image_path: str,
    model_path: str = MODEL_PATH,
    save_annotated: Optional[str] = None
):
    """
    Field Monitoring Agent
    ----------------------
    Input : field image path
    Output: dict for Agent-4
    """
    if not image_path or not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    model = _get_model(model_path)
    results = model(image_path)
    r = results[0]

    # Top prediction
    top_idx = r.probs.top1
    label = r.names[top_idx]
    confidence = float(r.probs.data[top_idx])

    # Save annotated image (for UI)
    if save_annotated:
        annotated = r.plot()
        cv2.imwrite(save_annotated, annotated)

    # Smoothed heuristics (better for Agent-4)
    if "weed" in label.lower():
        weed_percentage = int(confidence * 100)
    else:
        weed_percentage = int((1 - confidence) * 20)

    crop_stage = (
        "Ready for harvest"
        if any(k in label.lower() for k in ("ready", "ripe", "harvest"))
        else "Growing"
    )

    return {
        "field_label": label,
        "confidence": round(confidence, 3),
        "weed_percentage": weed_percentage,
        "crop_stage": crop_stage
    }


# ---------- Local test only ----------
if __name__ == "__main__":
    test_image = r"C:\Users\karth\OneDrive\Desktop\test_field.jpg"
    output = run_agent1(
        test_image,
        save_annotated="agent1_output.jpg"
    )
    print("Agent-1 Output:", output)

