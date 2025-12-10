import math
from collections import deque


class Agent:
    def __init__(self, start, goal, path, speed=2.0, color=(0, 1, 1), shape_type="sphere_droid", trail_length=20):
        self.start = start              
        self.goal = goal                
        self.path = path                
        self.speed = speed             
        self.color = color
        self.shape_type = shape_type
        self.path_i = 0                 
        self.position = (float(start[0]), 0.3, float(start[1]))
        
        # ✨ deque للأداء الأفضل
        self.trail_length = trail_length
        self.history = deque(maxlen=trail_length)
        
        self.arrived = False
        
        # ✨ تخزين آخر موقع لتجنب إضافة نقاط مكررة
        self._last_history_pos = None
        self._history_min_dist = 0.05  # الحد الأدنى للمسافة بين النقاط

    def update(self, dt):
        if self.arrived:
            return

        self.move(dt)

        # ✨ إضافة للـ history فقط إذا تحرك مسافة كافية
        if self._last_history_pos is None:
            self.history.append(self.position)
            self._last_history_pos = self.position
        else:
            dx = self.position[0] - self._last_history_pos[0]
            dz = self.position[2] - self._last_history_pos[2]
            dist = math.sqrt(dx*dx + dz*dz)
            
            if dist >= self._history_min_dist:
                self.history.append(self.position)
                self._last_history_pos = self.position

    def move(self, dt):
        if self.reached_goal():
            self.arrived = True
            return

        tx, ty = self.next_target()

        x, _, z = self.position
        dx = tx - x
        dz = ty - z

        dist = math.sqrt(dx*dx + dz*dz)

        if dist < 0.01:
            self.position = (float(tx), 0.3, float(ty))
            self.path_i += 1

            if self.reached_goal():
                self.arrived = True
            return

        step = self.speed * dt
        move_amount = min(step, dist)

        if dist > 1e-9:
            nx = x + (dx / dist) * move_amount
            nz = z + (dz / dist) * move_amount
        else:
            nx = tx
            nz = ty

        new_dx = tx - nx
        new_dz = ty - nz
        new_dist = math.sqrt(new_dx*new_dx + new_dz*new_dz)
        
        if new_dist < 0.005:
            self.position = (float(tx), 0.3, float(ty))
            self.path_i += 1
            if self.reached_goal():
                self.arrived = True
        else:
            self.position = (float(nx), 0.3, float(nz))

    def next_target(self):
        if self.path_i >= len(self.path):
            return self.goal
        return self.path[self.path_i]

    def reached_goal(self):
        return self.path_i >= len(self.path)