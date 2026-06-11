#!/usr/bin/env python3
"""Рисование на экране жестами руки через веб-камеру."""

from pathlib import Path
import time

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    HandLandmarksConnections,
    RunningMode,
)
from mediapipe.tasks.python.vision import drawing_utils as mp_drawing
from mediapipe.tasks.python.vision.drawing_utils import DrawingSpec

WIDTH, HEIGHT = 1280, 720
MODEL_PATH = Path(__file__).parent / "hand_landmarker.task"

COLORS = [
    (80, 80, 255),    # красный
    (255, 180, 100),  # голубой
    (255, 255, 255),  # белый
    (120, 255, 120),  # зелёный
]
COLOR_RADIUS = 22
COLOR_X = 40

LANDMARK_SPEC = DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3)
CONNECTION_SPEC = DrawingSpec(color=(0, 180, 255), thickness=2)


def finger_states(landmarks, handedness: str) -> list[bool]:
    """True = палец поднят."""
    tips = [4, 8, 12, 16, 20]
    pips = [3, 6, 10, 14, 18]

    fingers: list[bool] = []
    if handedness == "Right":
        fingers.append(landmarks[tips[0]].x > landmarks[pips[0]].x)
    else:
        fingers.append(landmarks[tips[0]].x < landmarks[pips[0]].x)

    for i in range(1, 5):
        fingers.append(landmarks[tips[i]].y < landmarks[pips[i]].y)

    return fingers


def is_open_palm(fingers: list[bool]) -> bool:
    """Все 5 пальцев подняты — не рисуем."""
    return all(fingers)


def is_drawing_gesture(fingers: list[bool]) -> bool:
    """Указательный вверх, средний, безымянный и мизинец сжаты."""
    _, index, middle, ring, pinky = fingers
    return index and not middle and not ring and not pinky


def is_fist(fingers: list[bool]) -> bool:
    """Все пальцы сжаты — режим ластика."""
    return not any(fingers)


def landmark_to_pixel(landmark, w: int, h: int) -> tuple[int, int]:
    return int(landmark.x * w), int(landmark.y * h)


def draw_color_palette(canvas: np.ndarray, active_idx: int) -> None:
    for i, color in enumerate(COLORS):
        cy = 120 + i * 70
        border = (200, 200, 200) if i == active_idx else (80, 80, 80)
        cv2.circle(canvas, (COLOR_X, cy), COLOR_RADIUS + 4, border, 3)
        cv2.circle(canvas, (COLOR_X, cy), COLOR_RADIUS, color, -1)


def hit_color_button(x: int, y: int) -> int | None:
    for i in range(len(COLORS)):
        cy = 120 + i * 70
        if (x - COLOR_X) ** 2 + (y - cy) ** 2 <= (COLOR_RADIUS + 8) ** 2:
            return i
    return None


def draw_hand_skeleton(frame: np.ndarray, hand_landmarks) -> None:
    mp_drawing.draw_landmarks(
        frame,
        hand_landmarks,
        HandLandmarksConnections.HAND_CONNECTIONS,
        landmark_drawing_spec=LANDMARK_SPEC,
        connection_drawing_spec=CONNECTION_SPEC,
    )


def main() -> None:
    if not MODEL_PATH.exists():
        print(f"Скачайте модель: wget -O {MODEL_PATH} "
              "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
              "hand_landmarker/float16/1/hand_landmarker.task")
        return

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

    if not cap.isOpened():
        print("Не удалось открыть веб-камеру")
        return

    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(MODEL_PATH)),
        running_mode=RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.7,
        min_hand_presence_confidence=0.6,
        min_tracking_confidence=0.6,
    )

    paint_layer = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    brush_color_idx = 0
    brush_thickness = 8
    eraser_thickness = 90
    prev_point: tuple[int, int] | None = None
    drawing = False
    erasing = False
    window = "Hand Paint"
    frame_ts = 0

    def on_mouse(event, x, y, _flags, _param):
        nonlocal brush_color_idx
        if event == cv2.EVENT_LBUTTONDOWN:
            idx = hit_color_button(x, y)
            if idx is not None:
                brush_color_idx = idx
            elif WIDTH - 160 <= x <= WIDTH - 20 and 20 <= y <= 70:
                paint_layer[:] = 0

    cv2.namedWindow(window)
    cv2.setMouseCallback(window, on_mouse)

    print("Управление:")
    print("  · Указательный вверх, остальные сжаты — рисовать")
    print("  · Кулак (все пальцы сжаты) — стирать")
    print("  · Ладонь раскрыта (5 пальцев) — пауза")
    print("  · Клик по цвету слева — сменить кисть")
    print("  · Clear / C — очистить, Q — выход")

    with HandLandmarker.create_from_options(options) as landmarker:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            frame_ts = int(time.time() * 1000)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result = landmarker.detect_for_video(mp_image, frame_ts)

            gesture_text = "Жест не распознан"
            tool_tip_px: tuple[int, int] | None = None

            if result.hand_landmarks and result.handedness:
                hand_lm = result.hand_landmarks[0]
                handedness = result.handedness[0][0].category_name
                fingers = finger_states(hand_lm, handedness)

                draw_hand_skeleton(frame, hand_lm)

                if is_open_palm(fingers):
                    gesture_text = "Ладонь открыта — пауза"
                    drawing = False
                    erasing = False
                    prev_point = None
                elif is_drawing_gesture(fingers):
                    gesture_text = "Рисую..."
                    tool_tip_px = landmark_to_pixel(hand_lm[8], w, h)
                    drawing = True
                    erasing = False
                    if prev_point is not None and tool_tip_px is not None:
                        cv2.line(
                            paint_layer,
                            prev_point,
                            tool_tip_px,
                            COLORS[brush_color_idx],
                            brush_thickness,
                            cv2.LINE_AA,
                        )
                    prev_point = tool_tip_px
                elif is_fist(fingers):
                    gesture_text = "Стираю..."
                    # Центр кулака стабильнее кончика пальца
                    tool_tip_px = landmark_to_pixel(hand_lm[9], w, h)
                    drawing = False
                    erasing = True
                    if tool_tip_px is not None:
                        cv2.circle(
                            paint_layer,
                            tool_tip_px,
                            eraser_thickness // 2,
                            (0, 0, 0),
                            -1,
                            cv2.LINE_AA,
                        )
                        if prev_point is not None:
                            cv2.line(
                                paint_layer,
                                prev_point,
                                tool_tip_px,
                                (0, 0, 0),
                                eraser_thickness,
                                cv2.LINE_AA,
                            )
                    prev_point = tool_tip_px
                else:
                    gesture_text = "Другой жест — пауза"
                    drawing = False
                    erasing = False
                    prev_point = None

                if tool_tip_px is not None:
                    if drawing:
                        ring_color = (0, 255, 0)
                    elif erasing:
                        ring_color = (0, 165, 255)  # оранжевый — ластик
                    else:
                        ring_color = (0, 0, 255)
                    cv2.circle(frame, tool_tip_px, 12, ring_color, 2)
            else:
                drawing = False
                erasing = False
                prev_point = None
                gesture_text = "Рука не видна"

            display = cv2.addWeighted(frame, 0.35, paint_layer, 0.65, 0)
            draw_color_palette(display, brush_color_idx)

            cv2.rectangle(display, (w - 160, 20), (w - 20, 70), (60, 140, 60), -1)
            cv2.rectangle(display, (w - 160, 20), (w - 20, 70), (200, 255, 200), 2)
            cv2.putText(display, "Clear", (w - 132, 58),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(display, gesture_text, (20, h - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)
            cv2.putText(display, "Hand Paint", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)

            cv2.imshow(window, display)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break
            if key == ord("c"):
                paint_layer[:] = 0
                prev_point = None

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
