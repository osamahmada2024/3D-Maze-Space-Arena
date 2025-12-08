import cv2
import math
import mediapipe as mp
from collections import deque
import platform  # أضفته لـ SYSTEM

from .MuteGestureDetector import MuteGestureDetector  # تصحيح: نسبي
from .DirectionGestureDetector import DirectionGestureDetector  # تصحيح: نسبي

SYSTEM = platform.system()

class HandGestureDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_face = mp.solutions.face_mesh
        self.drawer = mp.solutions.drawing_utils

        if SYSTEM == "Linux":
            self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        else:
            self.cap = cv2.VideoCapture(0)

        self.hands = self.mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
        self.face = self.mp_face.FaceMesh(max_num_faces=1)

        self.dir_detector = DirectionGestureDetector()
        self.mute_detector = MuteGestureDetector()
        self.queue = deque(maxlen=8)

    def run(self):
        while True:
            ok, frame = self.cap.read()
            if not ok:
                print("Camera NOT opened !!!")
                break

            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            hands = self.hands.process(rgb)
            face = self.face.process(rgb)

            right = left = None
            if hands.multi_hand_landmarks and hands.multi_handedness:
                for lms, handed in zip(hands.multi_hand_landmarks, hands.multi_handedness):
                    self.drawer.draw_landmarks(frame, lms, self.mp_hands.HAND_CONNECTIONS)
                    if handed.classification[0].label == "Right":
                        right = lms
                    else:
                        left = lms

            face_lms = None
            if face.multi_face_landmarks:
                face_lms = face.multi_face_landmarks[0]
                self.drawer.draw_landmarks(
                    frame, face_lms,
                    mp.solutions.face_mesh.FACEMESH_LIPS,
                    landmark_drawing_spec=mp.solutions.drawing_utils.DrawingSpec(
                        color=(0, 255, 0), thickness=1, circle_radius=0
                    ),
                    connection_drawing_spec=mp.solutions.drawing_utils.DrawingSpec(
                        color=(0, 255, 0), thickness=1
                    )
                )

            did_mute = self.mute_detector.detect_mute(right, left, face_lms, h, w)
            did_unmute = self.mute_detector.detect_unmute(right, left, face_lms, w, h)

            # Direction gestures
            if right:
                wrist = (right.landmark[0].x * w, right.landmark[0].y * h)
                mid = (right.landmark[9].x * w, right.landmark[9].y * h)
                size = math.hypot(mid[0] - wrist[0], mid[1] - wrist[1])
            else:
                size = 1

            gesture = self.dir_detector.detect(right, size, w, h)
            self.queue.append(gesture)
            gesture = max(self.queue, key=self.queue.count)

            if gesture != "Neutral" and not did_mute and not did_unmute:
                cv2.putText(frame, gesture, (40, 80), 1, 2, (0, 255, 0), 3)

            cv2.imshow("Gestures", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = HandGestureDetector()
    detector.run()