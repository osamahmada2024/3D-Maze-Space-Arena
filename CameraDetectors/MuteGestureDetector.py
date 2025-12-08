import math
import numpy as np
import mediapipe as mp

from .VolumeController import VolumeController  

class MuteGestureDetector:
    def __init__(self):
        self.volume = VolumeController()
        self.mp_hands = mp.solutions.hands

    def px(self, lm, w, h):
        return int(lm.x * w), int(lm.y * h)

    def finger_angle_vertical(self, mcp, tip):
        dx = tip[0] - mcp[0]
        dy = mcp[1] - tip[1]
        return abs(abs(math.degrees(math.atan2(dy, dx))) - 90)

    def detect_mute(self, right, left, face, h, w):
        mute_detected = False
        # X gesture
        if right and left:
            r = self.px(right.landmark[8], w, h)
            l = self.px(left.landmark[8], w, h)
            if math.hypot(r[0] - l[0], r[1] - l[1]) < 80:
                mute_detected = True

        # Finger on mouth
        if right and face:
            idx_tip = self.px(right.landmark[8], w, h)
            idx_mcp = self.px(right.landmark[5], w, h)
            angle = self.finger_angle_vertical(idx_mcp, idx_tip)
            top_lip = self.px(face.landmark[13], w, h)
            bot_lip = self.px(face.landmark[14], w, h)
            mouth = ((top_lip[0] + bot_lip[0]) // 2, (top_lip[1] + bot_lip[1]) // 2)
            if math.hypot(idx_tip[0] - mouth[0], idx_tip[1] - mouth[1]) < 55 and angle < 45:
                mute_detected = True

        if mute_detected and not self.volume.is_muted:
            self.volume.mute()
            return True

        return False

    def detect_unmute(self, right, left, face, w, h):
        if not self.volume.is_muted or not face:
            return False

        left_ear = self.px(face.landmark[234], w, h)
        right_ear = self.px(face.landmark[454], w, h)

        for hand in [right, left]:
            if hand:
                for fid in [4, 8, 12, 16, 20]:
                    tip = self.px(hand.landmark[fid], w, h)
                    if math.hypot(tip[0] - left_ear[0], tip[1] - left_ear[1]) < 20:
                        self.volume.unmute()
                        return True
                    if math.hypot(tip[0] - right_ear[0], tip[1] - right_ear[1]) < 20:
                        self.volume.unmute()
                        return True

        return False