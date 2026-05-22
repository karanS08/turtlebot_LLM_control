from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

import cv2
import numpy as np


@dataclass
class ColorDetection:
    color_name: str
    center: Tuple[int, int]
    area: float
    normalized_x: float
    normalized_size: float
    bounding_box: Tuple[int, int, int, int]


HSV_RANGES = {
    "red": [((0, 90, 70), (10, 255, 255)), ((170, 90, 70), (180, 255, 255))],
    "orange": [((8, 90, 80), (24, 255, 255))],
    "yellow": [((20, 80, 80), (38, 255, 255))],
    "green": [((40, 60, 50), (85, 255, 255))],
    "blue": [((90, 70, 50), (130, 255, 255))],
    "purple": [((130, 60, 50), (165, 255, 255))],
    "pink": [((145, 45, 80), (175, 255, 255))],
}


def detect_color_targets(
    bgr_image: np.ndarray,
    *,
    color_names: Iterable[str],
    search_window: Sequence[int],
    min_area: float = 250.0,
) -> Tuple[List[ColorDetection], dict, np.ndarray]:
    height, width = bgr_image.shape[:2]
    x_min, y_min, x_max, y_max = normalized_window(search_window, width, height)
    roi = bgr_image[y_min:y_max, x_min:x_max]
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    detections: List[ColorDetection] = []
    masks = {}
    combined_mask = np.zeros((height, width), dtype=np.uint8)

    for raw_name in color_names:
        color_name = str(raw_name).strip().lower()
        ranges = HSV_RANGES.get(color_name, HSV_RANGES["yellow"])
        roi_mask = np.zeros(hsv_roi.shape[:2], dtype=np.uint8)

        for lower, upper in ranges:
            roi_mask = cv2.bitwise_or(
                roi_mask,
                cv2.inRange(hsv_roi, np.array(lower), np.array(upper)),
            )

        kernel = np.ones((5, 5), dtype=np.uint8)
        roi_mask = cv2.morphologyEx(roi_mask, cv2.MORPH_OPEN, kernel)
        roi_mask = cv2.morphologyEx(roi_mask, cv2.MORPH_CLOSE, kernel)

        full_mask = np.zeros((height, width), dtype=np.uint8)
        full_mask[y_min:y_max, x_min:x_max] = roi_mask
        masks[color_name] = full_mask
        combined_mask = cv2.bitwise_or(combined_mask, full_mask)
        detections.extend(
            contour_detections(full_mask, color_name, width, height, min_area)
        )

    detections.sort(key=lambda detection: detection.area, reverse=True)
    return detections, masks, combined_mask


def contour_detections(
    mask: np.ndarray,
    color_name: str,
    width: int,
    height: int,
    min_area: float,
) -> List[ColorDetection]:
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    detections: List[ColorDetection] = []

    for contour in contours:
        area = float(cv2.contourArea(contour))
        if area < min_area:
            continue

        x, y, w, h = cv2.boundingRect(contour)
        center_x = x + w // 2
        center_y = y + h // 2
        normalized_x = ((center_x / max(width, 1)) - 0.5) * 2.0
        normalized_size = area / float(max(width * height, 1))
        detections.append(
            ColorDetection(
                color_name=color_name,
                center=(center_x, center_y),
                area=area,
                normalized_x=normalized_x,
                normalized_size=normalized_size,
                bounding_box=(x, y, w, h),
            )
        )

    return detections


def draw_detection_debug(
    bgr_image: np.ndarray,
    detections: Sequence[ColorDetection],
    combined_mask: np.ndarray,
    *,
    search_window: Sequence[int],
) -> np.ndarray:
    debug_image = bgr_image.copy()
    height, width = debug_image.shape[:2]
    x_min, y_min, x_max, y_max = normalized_window(search_window, width, height)
    cv2.rectangle(debug_image, (x_min, y_min), (x_max, y_max), (255, 255, 255), 1)

    mask_overlay = cv2.cvtColor(combined_mask, cv2.COLOR_GRAY2BGR)
    mask_overlay[:, :, 0] = 0
    mask_overlay[:, :, 1] = combined_mask
    mask_overlay[:, :, 2] = combined_mask
    debug_image = cv2.addWeighted(debug_image, 0.78, mask_overlay, 0.22, 0.0)

    for detection in detections:
        x, y, w, h = detection.bounding_box
        cv2.rectangle(debug_image, (x, y), (x + w, y + h), (0, 255, 255), 2)
        cv2.circle(debug_image, detection.center, 4, (0, 0, 255), -1)
        cv2.putText(
            debug_image,
            "%s %.2f" % (detection.color_name, detection.normalized_size),
            (x, max(y - 8, 16)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            1,
            cv2.LINE_AA,
        )

    return debug_image


def normalized_window(
    search_window: Sequence[int],
    width: int,
    height: int,
) -> Tuple[int, int, int, int]:
    if len(search_window) != 4:
        return 0, 0, width, height

    x_min, y_min, x_max, y_max = [int(value) for value in search_window]
    x_min = int(np.clip(x_min, 0, 100) * width / 100)
    y_min = int(np.clip(y_min, 0, 100) * height / 100)
    x_max = int(np.clip(x_max, 0, 100) * width / 100)
    y_max = int(np.clip(y_max, 0, 100) * height / 100)

    if x_max <= x_min or y_max <= y_min:
        return 0, 0, width, height
    return x_min, y_min, x_max, y_max
