import cv2

from ultralytics import YOLO
import supervision as sv
import numpy as np


def main():
    box_annotator = sv.BoundingBoxAnnotator()
    MAX_FRAMES_SINCE_SEEN = 30
    captured_ids = set()
    last_seen = {}

    model = YOLO("yolov8s.pt")
    for result in model.track(source=0, show=True, stream=True, agnostic_nms=True):
        frame = result.orig_img
        detections = sv.Detections.from_ultralytics(result)

        if result.boxes.id is not None: 
            detections.tracker_id = result.boxes.id.cpu().astype('int')
        
        current_detected_ids = set()
        labels = []

        for bbox, confidence, class_id, tracker_id in detections:
            labels = f"{tracker_id} {model.model.names[class_id]} {confidence:0.2f}"
            if class_id == 0:  
                current_detected_ids.add(tracker_id)
                last_seen[tracker_id] = 0  

                if tracker_id not in captured_ids:
                    x1, y1, x2, y2 = map(int, bbox[:4])
                    person_img = frame[y1:y2, x1:x2]
                    cv2.imwrite(f"person_{tracker_id}.jpg", person_img)
                    captured_ids.add(tracker_id)

        for tracker_id in list(last_seen.keys()):
            if tracker_id not in current_detected_ids:
                last_seen[tracker_id] += 1
            if last_seen[tracker_id] > MAX_FRAMES_SINCE_SEEN:
                del last_seen[tracker_id]
                if tracker_id in captured_ids:
                    captured_ids.remove(tracker_id)

        frame = box_annotator.annotate(
            scene = frame.copy(),
            detections = detections,
            labels = labels
        )

        cv2.imshow("Webcam", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == "__main__":
    main()