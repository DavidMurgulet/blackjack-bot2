from ultralytics import YOLO
import cv2


# Load the YOLO model with the specified weights
yolo = YOLO('best.pt')

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
        results = self.model([img], conf=0.30, save=True)
        names = results[0].names

    

# class DetectionModel:
#     def __init__(self, model_path):
#         self.model = YOLO(model_path)

#     def detect(self, img):
#         return self.model([img], conf=0.15, save=True)
    

# img = cv2.imread('test2.png')
# img = cv2.resize(img, (800, 800))


# # Run the model on the test image
# results = model([img], conf=0.15, save=True)

# # Extract the results
# boxes = results[0].boxes.xyxy.tolist()
# classes = results[0].boxes.cls.tolist()
# names = results[0].names
# confidences = results[0].boxes.conf.tolist()

# # Print the results
# print(f"Number of boxes detected: {len(boxes)}")
# print(f"Detected boxes: {boxes}")
# print(f"Detected classes: {classes}")
# print(f"Detected confidences: {confidences}")
# # Print the results
# print(f"Number of boxes detected: {len(boxes)}")
# print(f"Detected boxes: {boxes}")
# print(f"Detected classes: {classes}")
# print(f"Detected confidences: {confidences}")

# # Update the decision dictionary based on detected classes
# for cls in classes:
#     name = names[int(cls)]
#     if name in decision:
#         decision[name] = True
# # Update the decision dictionary based on detected classes
# for cls in classes:
#     name = names[int(cls)]
#     if name in decision:
#         decision[name] = True

# # Print the decision dictionary
# print(decision)
# # Print the decision dictionary
# print(decision)
