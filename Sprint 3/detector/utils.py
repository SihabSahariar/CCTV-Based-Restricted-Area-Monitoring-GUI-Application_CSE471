import numpy as np
import cv2


class_names = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
               'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
               'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
               'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
               'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
               'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
               'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard',
               'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase',
               'scissors', 'teddy bear', 'hair drier', 'toothbrush']

# Create a list of colors for each class where each color is a tuple of 3 integer values
rng = np.random.default_rng(3)
colors = rng.uniform(0, 255, size=(len(class_names), 3))


def nms(boxes, scores, iou_threshold):
    # Sort by score
    sorted_indices = np.argsort(scores)[::-1]

    keep_boxes = []
    while sorted_indices.size > 0:
        # Pick the last box
        box_id = sorted_indices[0]
        keep_boxes.append(box_id)

        # Compute IoU of the picked box with the rest
        ious = compute_iou(boxes[box_id, :], boxes[sorted_indices[1:], :])

        # Remove boxes with IoU over the threshold
        keep_indices = np.where(ious < iou_threshold)[0]

        # print(keep_indices.shape, sorted_indices.shape)
        sorted_indices = sorted_indices[keep_indices + 1]

    return keep_boxes


def compute_iou(box, boxes):
    # Compute xmin, ymin, xmax, ymax for both boxes
    xmin = np.maximum(box[0], boxes[:, 0])
    ymin = np.maximum(box[1], boxes[:, 1])
    xmax = np.minimum(box[2], boxes[:, 2])
    ymax = np.minimum(box[3], boxes[:, 3])

    # Compute intersection area
    intersection_area = np.maximum(0, xmax - xmin) * np.maximum(0, ymax - ymin)

    # Compute union area
    box_area = (box[2] - box[0]) * (box[3] - box[1])
    boxes_area = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    union_area = box_area + boxes_area - intersection_area

    # Compute IoU
    iou = intersection_area / union_area

    return iou


def xywh2xyxy(x):
    # Convert bounding box (x, y, w, h) to bounding box (x1, y1, x2, y2)
    y = np.copy(x)
    y[..., 0] = x[..., 0] - x[..., 2] / 2
    y[..., 1] = x[..., 1] - x[..., 3] / 2
    y[..., 2] = x[..., 0] + x[..., 2] / 2
    y[..., 3] = x[..., 1] + x[..., 3] / 2
    return y

def draw_detections_bbox(image, boxes, scores, class_ids, mask_alpha=0.3):
    mask_img = image.copy()
    det_img = image.copy()

    img_height, img_width = image.shape[:2]
    size = min([img_height, img_width]) * 0.0006
    text_thickness = int(min([img_height, img_width]) * 0.001)

    # Draw bounding boxes and labels of detections
    for box, score, class_id in zip(boxes, scores, class_ids):
        color = colors[2]

        # x1, y1, x2, y2 = box.astype(int)

        # if class_id == 1 or class_id ==2 or class_id==3 or class_id==5 or class_id ==7 or class_id == 9:
        if class_id== 0:

            x1, y1, x2, y2 = box.tolist()#.astype(int)
            x1,y1,x2,y2 = int(x1),int(y1),int(x2),int(y2)
            # print(box,x1,y1,x2,y2)

            # Draw rectangle
            cv2.rectangle(det_img, (x1, y1), (x2, y2), color, 2)

            # Draw fill rectangle in mask image
            cv2.rectangle(mask_img, (x1, y1), (x2, y2), color, -1)

    return cv2.addWeighted(mask_img, mask_alpha, det_img, 1 - mask_alpha, 0)



def draw_detections_bbox_nofill(image, boxes, scores, class_ids,poslist,ids=None):
    det_img = image.copy()
    posList = poslist
    all_result = check_overlap_and_percentage_nofill(boxes,posList)
    img_height, img_width = image.shape[:2]
    size = min([img_height, img_width]) * 0.0006
    text_thickness = int(min([img_height, img_width]) * 0.001)
    lst_track_id = []
    if ids is not None:
        for box, occ,class_id,track_id in zip(boxes,all_result, class_ids,ids):
            color = colors[2]
            x1, y1, x2, y2 = box.tolist()#.astype(int)
            x1,y1,x2,y2 = int(x1),int(y1),int(x2),int(y2)
            occ = False
            if class_id== 0: # Person class only
                if occ==False:
                    det_img = cv2.rectangle(det_img, (x1, y1), (x2, y2), color, 2)
                    caption = f"Safe Area"
                    (tw, th), _ = cv2.getTextSize(text=caption, fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=size, thickness=text_thickness)
                    th = int(th * 1.2)
                    det_img = cv2.putText(det_img, caption, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, size, (255, 255, 255), text_thickness, cv2.LINE_AA)
                    
                # det_img = cv2.putText(det_img, "Track ID : "+ str(track_id), (x1, y1+10), cv2.FONT_HERSHEY_SIMPLEX, size, (255, 255, 255), text_thickness, cv2.LINE_AA)
                # else:
                    det_img = add_track_id(det_img, track_id, x1, y1-20, font_scale=0.5, font_thickness=1, bg_color=(0, 0, 255), text_color=(255, 255, 255), arrow_length=20)
                else:
                    lst_track_id.append(track_id)
                    
        return det_img,lst_track_id

    else:
        for box, occ,class_id in zip(boxes,all_result, class_ids):
            color = colors[2]
            x1, y1, x2, y2 = box.tolist()
            x1,y1,x2,y2 = int(x1),int(y1),int(x2),int(y2)
            occ = False
            if class_id== 0: # Person class only
                if occ==False:
                    det_img = cv2.rectangle(det_img, (x1, y1), (x2, y2), color, 2)
                    caption = f"Safe Area"
                    (tw, th), _ = cv2.getTextSize(text=caption, fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=size, thickness=text_thickness)
                    th = int(th * 1.2)
                    det_img = cv2.putText(det_img, caption, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, size, (255, 255, 255), text_thickness, cv2.LINE_AA)
        return det_img,lst_track_id

def add_track_id(image, track_id, x, y, font_scale=0.5, font_thickness=1, bg_color=(0, 0, 255), text_color=(255, 255, 255), arrow_length=20):
    output_image = image.copy()
    text = "Track ID : " + str(track_id)
    (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
    # Calculate the position of the background rectangle
    rect_x1, rect_y1 = x, y
    rect_x2, rect_y2 = x + text_width, y - text_height - baseline
    # Draw a filled rectangle as the background
    cv2.rectangle(output_image, (rect_x1, rect_y1), (rect_x2, rect_y2), bg_color, -1)
    # Draw the text on top of the background
    cv2.putText(output_image, text, (x, y - baseline), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness, cv2.LINE_AA)
    # Draw an arrow pointing to the text
    # arrow_end = (rect_x1 + (rect_x2 - rect_x1) // 2, rect_y2)
    # arrow_start = (x + (text_width // 2), y - baseline - arrow_length)
    # cv2.arrowedLine(output_image, arrow_start, arrow_end, text_color, 1, tipLength=0.1)
    return output_image

def draw_detections(image, boxes, scores, class_ids,posList ,mask_alpha=0.3):
    mask_img = image.copy()
    det_img = image.copy()
    posList = posList

    img_height, img_width = image.shape[:2]
    size = min([img_height, img_width]) * 0.0006
    text_thickness = int(min([img_height, img_width]) * 0.001)
    all_result = check_overlap_and_percentage(posList,boxes.tolist())
    # print(all_perc)

    # Draw bounding boxes and labels of detections
    for pos, occ in zip(posList, all_result):
        

        # x1, y1, x2, y2 = box.astype(int)
        x1,y1,x2,y2 = pos
        # print(perc)
        if occ==True:
            color = (255,0,0)
            
            # Draw rectangle
            cv2.rectangle(det_img, (x1, y1), (x2, y2), color, 2)

            # Draw fill rectangle in mask image
            cv2.rectangle(mask_img, (x1, y1), (x2, y2), color, -1)

            # caption = f'{label} {int(score * 100)}%'
            caption = "Occupied"
            (tw, th), _ = cv2.getTextSize(text=caption, fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=size, thickness=text_thickness)
            th = int(th * 1.2)

            cv2.rectangle(det_img, (x1, y1), (x1 + tw, y1 - th), color, -1)
            cv2.rectangle(mask_img, (x1, y1), (x1 + tw, y1 - th), color, -1)
            cv2.putText(det_img, caption, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, size, (255, 255, 255), text_thickness, cv2.LINE_AA)

            cv2.putText(mask_img, caption, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, size, (255, 255, 255), text_thickness, cv2.LINE_AA)
        else:
            color = (0,255,0)
            
            # Draw rectangle
            cv2.rectangle(det_img, (x1, y1), (x2, y2), color, 2)

            # Draw fill rectangle in mask image
            cv2.rectangle(mask_img, (x1, y1), (x2, y2), color, -1)

            # caption = f'{label} {int(score * 100)}%'
            caption = "Unoccupied"
            (tw, th), _ = cv2.getTextSize(text=caption, fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                        fontScale=size, thickness=text_thickness)
            th = int(th * 1.2)

            cv2.rectangle(det_img, (x1, y1),
                        (x1 + tw, y1 - th), color, -1)
            cv2.rectangle(mask_img, (x1, y1),
                        (x1 + tw, y1 - th), color, -1)
            cv2.putText(det_img, caption, (x1, y1),
                        cv2.FONT_HERSHEY_SIMPLEX, size, (255, 255, 255), text_thickness, cv2.LINE_AA)

            cv2.putText(mask_img, caption, (x1, y1),
                        cv2.FONT_HERSHEY_SIMPLEX, size, (255, 255, 255), text_thickness, cv2.LINE_AA)

    return cv2.addWeighted(mask_img, mask_alpha, det_img, 1 - mask_alpha, 0)


def draw_comparison(img1, img2, name1, name2, fontsize=2.6, text_thickness=3):
    (tw, th), _ = cv2.getTextSize(text=name1, fontFace=cv2.FONT_HERSHEY_DUPLEX,
                                  fontScale=fontsize, thickness=text_thickness)
    x1 = img1.shape[1] // 3
    y1 = th
    offset = th // 5
    cv2.rectangle(img1, (x1 - offset * 2, y1 + offset),
                  (x1 + tw + offset * 2, y1 - th - offset), (0, 115, 255), -1)
    cv2.putText(img1, name1,
                (x1, y1),
                cv2.FONT_HERSHEY_DUPLEX, fontsize,
                (255, 255, 255), text_thickness)


    (tw, th), _ = cv2.getTextSize(text=name2, fontFace=cv2.FONT_HERSHEY_DUPLEX,
                                  fontScale=fontsize, thickness=text_thickness)
    x1 = img2.shape[1] // 3
    y1 = th
    offset = th // 5
    cv2.rectangle(img2, (x1 - offset * 2, y1 + offset),
                  (x1 + tw + offset * 2, y1 - th - offset), (94, 23, 235), -1)

    cv2.putText(img2, name2,
                (x1, y1),
                cv2.FONT_HERSHEY_DUPLEX, fontsize,
                (255, 255, 255), text_thickness)

    combined_img = cv2.hconcat([img1, img2])
    if combined_img.shape[1] > 3840:
        combined_img = cv2.resize(combined_img, (3840, 2160))

    return combined_img

def calculate_overlap_percentage(rect1, rect2):
    # Calculate the area of each rectangle
    area_rect1 = (rect1[2] - rect1[0]) * (rect1[3] - rect1[1])
    area_rect2 = (rect2[2] - rect2[0]) * (rect2[3] - rect2[1])

    # Calculate the coordinates of the intersection rectangle
    x1_inter = max(rect1[0], rect2[0])
    y1_inter = max(rect1[1], rect2[1])
    x2_inter = min(rect1[2], rect2[2])
    y2_inter = min(rect1[3], rect2[3])

    # Check if there is an intersection
    if x1_inter < x2_inter and y1_inter < y2_inter:
        # Calculate the area of the intersection rectangle
        area_intersection = (x2_inter - x1_inter) * (y2_inter - y1_inter)
    else:
        # No intersection
        area_intersection = 0

    # Calculate the percentage of overlap
    overlap_percentage = (area_intersection / min(area_rect1, area_rect2)) * 100

    return overlap_percentage


# Calculate the overlap percentage between two lists of rectangles
def check_overlap_and_percentage(A, B, threshold=40):
    overlap_flags = []
    for rect1 in A:
        overlaps = any(
            calculate_overlap_percentage(rect1, rect2) > threshold
            for rect2 in B
        )
        overlap_flags.append(overlaps)
    return overlap_flags


def check_overlap_and_percentage_nofill(A, B, threshold=50):
    overlap_flags = []
    for rect1 in A:
        overlaps = any(
            calculate_overlap_percentage(rect1, rect2) > threshold
            for rect2 in B
        )
        overlap_flags.append(overlaps)
    return overlap_flags

def check_overlap_flag(rect1, rect2, threshold=40):
    overlap = calculate_overlap_percentage(rect1, rect2)
    return overlap > threshold

def putBText(img, text, text_offset_x=20, text_offset_y=20, vspace=10, hspace=10, font_scale=1.5,
             background_RGB=(255, 255, 255), text_RGB=(1, 1, 1), font=cv2.FONT_HERSHEY_DUPLEX,
             thickness=2, alpha=0.6, gamma=0, border_thickness=2, border_RGB=(0, 0, 0)):

    R, G, B = background_RGB[0], background_RGB[1], background_RGB[2]
    text_R, text_G, text_B = text_RGB[0], text_RGB[1], text_RGB[2]
    (text_width, text_height) = cv2.getTextSize(text, font, fontScale=font_scale, thickness=thickness)[0]
    x, y, w, h = text_offset_x, text_offset_y, text_width, text_height
    crop = img[y - vspace:y + h + vspace, x - hspace:x + w + hspace]
    white_rect = np.ones(crop.shape, dtype=np.uint8) * 255
    rect_changed = white_rect.copy()
    res = cv2.addWeighted(crop, alpha, rect_changed, 1 - alpha, gamma)
    border_color = border_RGB[::-1]
    cv2.rectangle(res, (0, 0), (res.shape[1], res.shape[0]), border_color, border_thickness)
    img[y - vspace:y + vspace + h, x - hspace:x + hspace + w] = res
    cv2.putText(img, u"{}".format(text), (x, y + h), font, fontScale=font_scale, color=(text_B, text_G, text_R), thickness=thickness)
    return img

def draw_bbox(image, position = None, color = None, text =None, mask_alpha=0.3):
    mask_img = image.copy()
    det_img = image.copy()

    img_height, img_width = image.shape[:2]
    size = min([img_height, img_width]) * 0.0006
    text_thickness = int(min([img_height, img_width]) * 0.001)
    # print(all_perc)

    # x1, y1, x2, y2 = box.astype(int)
    x1,y1,x2,y2 = position
    # print(perc)

    # Draw rectangle
    cv2.rectangle(det_img, (x1, y1), (x2, y2), color, 2)

    # Draw fill rectangle in mask image
    cv2.rectangle(mask_img, (x1, y1), (x2, y2), color, -1)

    # caption = f'{label} {int(score * 100)}%'
    caption = text
    (tw, th), _ = cv2.getTextSize(text=caption, fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=size, thickness=text_thickness)
    th = int(th * 1.2)

    cv2.rectangle(det_img, (x1, y1), (x1 + tw, y1 - th), color, -1)
    cv2.rectangle(mask_img, (x1, y1), (x1 + tw, y1 - th), color, -1)
    cv2.putText(det_img, caption, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, size, (255, 255, 255), text_thickness, cv2.LINE_AA)

    cv2.putText(mask_img, caption, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, size, (255, 255, 255), text_thickness, cv2.LINE_AA)
 

    return cv2.addWeighted(mask_img, mask_alpha, det_img, 1 - mask_alpha, 0)