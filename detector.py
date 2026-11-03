import os

from ultralytics import YOLO

# Where the dental models will be placed (Model A for X-rays, Model B for photos).
MODEL_PATHS = {
    "X-ray": "models/xray_best.pt",
    "Photo": "models/photo_best.pt",
}

# Used when a dental model file is not available yet.
FALLBACK_MODEL = "yolov8n.pt"

# Ignore detections below this confidence (0.25 means 25 percent).
MIN_CONFIDENCE = 0.25

# Models that are already loaded are kept here, so we load each one only once.
loaded_models = {}


def clean_name(name):
    """Make a class name match the keys in RULES.

    Example: "Periapical_Lesion" becomes "periapical lesion".
    """
    name = name.lower()
    name = name.replace("_", " ").replace("-", " ")
    return " ".join(name.split())


def get_model(input_type):
    """Return the model for the given input type ("X-ray" or "Photo")."""
    if input_type in loaded_models:
        return loaded_models[input_type]

    path = MODEL_PATHS[input_type]
    if not os.path.exists(path):
        path = FALLBACK_MODEL

    model = YOLO(path)
    loaded_models[input_type] = model
    return model


def detect(image, input_type):
    """Run the right model on a PIL image.

    Returns two things:
    1. a list of (name, confidence) pairs
    2. the same image with boxes drawn on it (in BGR color order)
    """
    model = get_model(input_type)
    results = model(image, conf=MIN_CONFIDENCE)
    result = results[0]

    found = []
    for box in result.boxes:
        class_id = int(box.cls[0])
        name = clean_name(result.names[class_id])
        confidence = float(box.conf[0])
        found.append((name, confidence))

    # plot() draws the boxes and labels and returns the image as an array
    annotated = result.plot()

    return found, annotated