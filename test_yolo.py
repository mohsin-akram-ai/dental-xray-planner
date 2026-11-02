from ultralytics import YOLO

model = YOLO("yolov8n.pt")
results = model("https://ultralytics.com/images/bus.jpg")
result = results[0]

for box in result.boxes:
    class_id = int(box.cls[0])
    name = result.names[class_id]
    confidence = float(box.conf[0])
    print(name, round(confidence * 100, 1), "%")

result.save(filename="test_result.jpg")
print("Done. Check test_result.jpg")