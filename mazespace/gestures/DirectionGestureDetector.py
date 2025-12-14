import math
import numpy as np
import mediapipe as mp

class DirectionGestureDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands

    def px(self, lm, w, h):
        return int(lm.x * w), int(lm.y * h)

    def tip_mcp_dist(self, tip, mcp):
        return math.hypot(tip[0] - mcp[0], tip[1] - mcp[1])

    def detect(self, hand_lms, hand_size, w, h):
        if not hand_lms:
            return "Neutral"

        mp_h = self.mp_hands.HandLandmark
        tips = {}
        mcps = {}

        fingers = [
            ("thumb", mp_h.THUMB_TIP, mp_h.THUMB_MCP),
            ("index", mp_h.INDEX_FINGER_TIP, mp_h.INDEX_FINGER_MCP),
            ("middle", mp_h.MIDDLE_FINGER_TIP, mp_h.MIDDLE_FINGER_MCP),
            ("ring", mp_h.RING_FINGER_TIP, mp_h.RING_FINGER_MCP),
            ("pinky", mp_h.PINKY_TIP, mp_h.PINKY_MCP)
        ]

        for f, tip_id, mcp_id in fingers:
            tips[f] = self.px(hand_lms.landmark[tip_id], w, h)
            mcps[f] = self.px(hand_lms.landmark[mcp_id], w, h)

        d = {f: self.tip_mcp_dist(tips[f], mcps[f]) for f in tips}

        folded_thresh = 0.65 * hand_size
        length_thresh = 0.50 * hand_size

        folded = {f: d[f] < folded_thresh for f in d}

        if sum(folded.values()) >= 4:
            return "Closed"

        if not folded["index"]:
            dx = -(tips["index"][0] - mcps["index"][0])
            dy = mcps["index"][1] - tips["index"][1]
            length = math.hypot(dx, dy)

            if length >= length_thresh:
                angle = math.degrees(math.atan2(dy, dx))
                if -45 <= angle <= 45:
                    return "Left"
                elif 45 < angle <= 135:
                    return "Up"
                elif angle > 135 or angle < -135:
                    return "Right"
                else:
                    return "Down"

        return "Neutral"