"""
HandGestureDetector.py - Hand Gesture Detection System
Detects hand gestures using MediaPipe for game control
"""

import cv2
import math
import mediapipe as mp
import platform
from collections import deque

# Import gesture detectors from same package
try:
    # Try relative import (if in gestures/ package)
    from .MuteGestureDetector import MuteGestureDetector
    from .DirectionGestureDetector import DirectionGestureDetector
except ImportError:
    # Try absolute import (if running standalone)
    from MuteGestureDetector import MuteGestureDetector
    from DirectionGestureDetector import DirectionGestureDetector

SYSTEM = platform.system()


class HandGestureDetector:
    """
    Main hand gesture detector.
    Combines direction gestures and mute gestures.
    """
    
    def __init__(self):
        """Initialize gesture detection system."""
        # MediaPipe components
        self.mp_hands = mp.solutions.hands
        self.mp_face = mp.solutions.face_mesh
        self.drawer = mp.solutions.drawing_utils

        # Camera setup (platform-specific)
        if SYSTEM == "Linux":
            self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        else:
            self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            print("[WARNING] Camera not available")

        # Hand and face detection
        self.hands = self.mp_hands.Hands(
            max_num_hands=2, 
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.face = self.mp_face.FaceMesh(
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Gesture detectors
        self.dir_detector = DirectionGestureDetector()
        self.mute_detector = MuteGestureDetector()
        
        # Gesture smoothing queue
        self.queue = deque(maxlen=8)
        
        # State
        self.current_gesture = "Neutral"
        self.is_running = False

    def process_frame(self):
        """
        Process a single frame from camera.
        
        Returns:
            tuple: (frame, gesture, did_mute, did_unmute)
        """
        ok, frame = self.cap.read()
        if not ok:
            return None, "Neutral", False, False

        # Flip for mirror effect
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        # Convert to RGB for MediaPipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hands_result = self.hands.process(rgb)
        face_result = self.face.process(rgb)

        # Extract hand landmarks
        right_hand = None
        left_hand = None
        
        if hands_result.multi_hand_landmarks and hands_result.multi_handedness:
            for lms, handed in zip(hands_result.multi_hand_landmarks, 
                                  hands_result.multi_handedness):
                # Draw landmarks
                self.drawer.draw_landmarks(
                    frame, lms, self.mp_hands.HAND_CONNECTIONS
                )
                
                # Identify left/right hand
                label = handed.classification[0].label
                if label == "Right":
                    right_hand = lms
                else:
                    left_hand = lms

        # Extract face landmarks
        face_lms = None
        if face_result.multi_face_landmarks:
            face_lms = face_result.multi_face_landmarks[0]
            
            # Draw lips
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

        # Detect mute/unmute gestures
        did_mute = self.mute_detector.detect_mute(right_hand, left_hand, face_lms, h, w)
        did_unmute = self.mute_detector.detect_unmute(right_hand, left_hand, face_lms, w, h)

        # Detect direction gestures (only with right hand)
        gesture = "Neutral"
        if right_hand:
            # Calculate hand size
            wrist = (right_hand.landmark[0].x * w, right_hand.landmark[0].y * h)
            middle_mcp = (right_hand.landmark[9].x * w, right_hand.landmark[9].y * h)
            hand_size = math.hypot(
                middle_mcp[0] - wrist[0], 
                middle_mcp[1] - wrist[1]
            )
            
            gesture = self.dir_detector.detect(right_hand, hand_size, w, h)
        
        # Smooth gesture detection
        self.queue.append(gesture)
        gesture = max(self.queue, key=self.queue.count)

        # Display gesture on screen (if not muting)
        if gesture != "Neutral" and not did_mute and not did_unmute:
            cv2.putText(
                frame, gesture, (40, 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3
            )

        return frame, gesture, did_mute, did_unmute

    def run(self):
        """
        Run the gesture detection loop.
        Displays camera feed with detected gestures.
        """
        self.is_running = True
        print("[GESTURE] Starting gesture detection...")
        print("[GESTURE] Press ESC to exit")
        
        while self.is_running:
            frame, gesture, did_mute, did_unmute = self.process_frame()
            
            if frame is None:
                print("[ERROR] Camera not available")
                break
            
            # Display frame
            cv2.imshow("Hand Gestures", frame)
            
            # Check for exit
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
        
        self.cleanup()

    def get_current_gesture(self):
        """
        Get current detected gesture without display.
        
        Returns:
            str: Current gesture ("Up", "Down", "Left", "Right", "Neutral", "Closed")
        """
        _, gesture, _, _ = self.process_frame()
        return gesture

    def cleanup(self):
        """Release camera and close windows."""
        self.is_running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("[GESTURE] Cleanup complete")

    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()


if __name__ == "__main__":
    # Test the gesture detector
    detector = HandGestureDetector()
    detector.run()