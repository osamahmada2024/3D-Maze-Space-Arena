import math
from collections import deque


class Agent:
    def __init__(self, start, goal, path, speed=2.0, color=(0, 1, 1), shape_type="sphere_droid", 
                 trail_length=20, algo_name="Unknown", execution_time=0.0):
        self.start = start              
        self.goal = goal                
        self.path = path                
        self.speed = speed             
        self.color = color
        self.shape_type = shape_type
        self.algo_name = algo_name
        self.execution_time = execution_time
        
        # ✨ Timing (Seconds)
        self.travel_start_time = None
        self.travel_finish_time = None
        self.travel_time = 0.0
        
        self.path_i = 0                 
        self.position = (float(start[0]), 0.3, float(start[1]))
        self.steps_taken = 0
        self.visited_cells = set()
        self.visited_cells.add(start)
        
        # ✨ deque للأداء الأفضل
        self.trail_length = trail_length
        self.history = deque(maxlen=trail_length)
        
        self.arrived = False
        self.stuck = False # NEW: Track if path complete but goal not reached
        
        # ✨ تخزين آخر موقع لتجنب إضافة نقاط مكررة
        self._last_history_pos = None
        self._history_min_dist = 0.05

    def update(self, dt):
        # Start timer on first update
        if self.travel_start_time is None:
            self.travel_start_time = time.time()
            
        if self.arrived or self.stuck:
            return

        self.move(dt)

        # ✨ إضافة للـ history
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
            self._mark_arrival()
            return

        tx, ty = self.next_target()
        
        # If no more targets but not reached goal -> Stuck
        if tx is None:
            self.stuck = True
            return

        x, _, z = self.position
        dx = tx - x
        dz = ty - z

        dist = math.sqrt(dx*dx + dz*dz)

        if dist < 0.01:
            self.position = (float(tx), 0.3, float(ty))
            self.path_i += 1
            self.steps_taken += 1
            if self.path_i < len(self.path):
                self.visited_cells.add(self.path[self.path_i])

            if self.reached_goal():
                self._mark_arrival()
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
            self.steps_taken += 1
            if self.path_i < len(self.path):
                self.visited_cells.add(self.path[self.path_i])
            if self.reached_goal():
                self._mark_arrival()
        else:
            self.position = (float(nx), 0.3, float(nz))

    def next_target(self):
        if self.path_i >= len(self.path):
            return None, None # End of path
        return self.path[self.path_i]

    def reached_goal(self):
        # Strict validation: Must be physically close to GOAL
        dx = self.position[0] - self.goal[0]
        dz = self.position[2] - self.goal[1]
        dist_to_goal = math.sqrt(dx*dx + dz*dz)
        return dist_to_goal < 0.5

    def _mark_arrival(self):
        if not self.arrived:
            self.arrived = True
            self.travel_finish_time = time.time()
            self.travel_time = self.travel_finish_time - self.travel_start_time