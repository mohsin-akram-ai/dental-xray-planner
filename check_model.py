from detector import clean_name
from rules import RULES
from ultralytics import YOLO

# Change this one line to check another model, for example "models/xray_best.pt".
MODEL_FILE = "yolov8n.pt"

model = YOLO(MODEL_FILE)

# Clean every class name the same way detector.py does.
names = [clean_name(name) for name in model.names.values()]

matched = []
unmatched = []
for name in names:
    if name in RULES:
        matched.append(name)
    else:
        unmatched.append(name)

print("Model file:", MODEL_FILE)
print("Number of classes:", len(names))
print("Class names:", names)
print("Names that have a treatment rule:", matched)
print("Names with NO rule yet:", unmatched)