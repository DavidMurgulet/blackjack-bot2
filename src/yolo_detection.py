from ultralytics import YOLO
import cv2


# Load the YOLO model with the specified weights
# yolo = YOLO('best.pt') already done in self.model?


class DetectionModel:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.detection = {
            "hit": False,
            "stand": False,
            "double": False,
            "split": False,
            "bet_button": False,
            "bet_one": False,
            "bet_five": False,
            "bet_ten": False,
            # TODO: Add more bet options
        }

    def detect(self, img):
        results = self.model([img], conf=0.20, save=False)
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
                self.detection["hit"] = True
                self.detection["hit_location"] = (center_x, center_y)
            elif name == "stand":
                self.detection["stand"] = True
                self.detection["stand_location"] = (center_x, center_y)
            elif name == "double":
                self.detection["double"] = True
                self.detection["double_location"] = (center_x, center_y)
            elif name == "split":
                self.detection["split"] = True
                self.detection["split_location"] = (center_x, center_y)
            elif name == "bet_button":
                self.detection["bet_button"] = True
                self.detection["bet_button_location"] = (center_x, center_y)
            elif name == "bet_one":
                self.detection["bet_one"] = True
                self.detection["bet_one_location"] = (center_x, center_y)
            elif name == "bet_five":
                self.detection["bet_five"] = True
                self.detection["bet_five_location"] = (center_x, center_y)
            elif name == "bet_ten":
                self.detection["bet_ten"] = True
                self.detection["bet_ten_location"] = (center_x, center_y)

        # evrerytime we run yolo the detection will be updated.  
        return self.detection