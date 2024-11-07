from ultralytics import YOLO

model = YOLO('data/weights/best.pt')

decision = {
            "hit": False,
            "stand": False,
            "double": False,
            "split": False,
            "bet_button": False, 
            "bet_one": False,
            "bet_five": False,
            "bet_ten": False,
        }

results = model(['data/test_images/bet_test1.png'], conf=0.3, save=True)
boxes = results[0].boxes.xyxy.tolist()
classes = results[0].boxes.cls.tolist()
names = results[0].names
confidences = results[0].boxes.conf.tolist()

for box, cls, conf in zip(boxes, classes, confidences):
    x1, y1, x2, y2 = box
    
    center_x = (x1+x2) / 2
    center_y = (y1+y2) / 2

    confidence = conf
    detected_class = cls
    name = names[int(cls)]
    
    if name == "hit":
        decision["hit"] = True
        decision["hit_location"] = (center_x, center_y)
        decision["hit_confidence"] = confidence
    elif name == "stand":
        decision["stand"] = True
        decision["stand_location"] = (center_x, center_y)
        decision["stand_confidence"] = confidence
    elif name == "double":
        decision["double"] = True
        decision["double_location"] = (center_x, center_y)
        decision["double_confidence"] = confidence
    elif name == "split":
        decision["split"] = True
        decision["split_location"] = (center_x, center_y)
        decision["split_confidence"] = confidence
    elif name == "bet_button":
        decision["bet_button"] = True
        decision["bet_button_location"] = (center_x, center_y)
        decision["bet_button_confidence"] = confidence
    elif name == "bet_one":
        decision["bet_one"] = True
        decision["bet_one_location"] = (center_x, center_y)
        decision["bet_one_confidence"] = confidence
    elif name == "bet_five":
        decision["bet_five"] = True
        decision["bet_five_location"] = (center_x, center_y)
        decision["bet_five_confidence"] = confidence
    elif name == "bet_ten":
        decision["bet_ten"] = True
        decision["bet_ten_location"] = (center_x, center_y)
        decision["bet_ten_confidence"] = confidence

print(decision)