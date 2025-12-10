import time
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from core.Scene import Scene
from core.Agent import Agent
from core.GridUtils import GridUtils
from rendering.GoalRender import GoalRender
from rendering.PathRender import PathRender
from core.GridGenerator import GridGenerator
from rendering.AgentRender import AgentRender
from ui.CameraController import CameraController
from core.PathfindingEngine import PathfindingEngine
from rendering.EnvironmentRender import EnvironmentRender3D

class SpaceScene(Scene):
    def __init__(self, selected_shape, selected_algo,
                 #### 3amak osama ####
                    selected_Gamemode
                #### 3amak osama ####
                 , width, height):
        
        self.selected_shape = selected_shape
        self.selected_algo = selected_algo
        ### 3amak osama ####
        self.selected_Gamemode = selected_Gamemode
        ### 3amak osama ####
        self.width = width
        self.height = height
        
        self.grid_size = 25
        self.cell_size = 1.0
        self.obstacle_prob = 0.25
        
        self.agent = None
        self.grid = None
        self.camera = None
        
        # Renderers
        self.environment_renderer = None
        self.agent_renderer = None
        self.path_renderer = None
        self.goal_renderer = None
        
        self.start_time = 0
        self.game_active = False

        #### 3amak osama ####
        # determine if this scene should allow manual/player controls
        # GameMode expected values: "PlayerVsAI", "PlayerVsPlayer", "AIvsAI"
        # manual_controls == True when PlayerVsPlayer
        self.manual_controls = (str(self.selected_Gamemode) == "PlayerVsPlayer")
        #### 3amak osama ####

    def initialize(self):
        # OpenGL Setup
        self._init_opengl()
        
        # Grid Generation
        generator = GridGenerator(self.grid_size, self.obstacle_prob)
        self.grid = generator.generate()
        
        start = (0, 0)
        goal = (self.grid_size-1, self.grid_size-1)

        #### 3amak osama ####
        # store start/goal on the instance so other methods (update) can access them
        self.start = start
        self.goal = goal
        #### 3amak osama ####
        
        # Ensure start/goal are clear
        self.grid[start[1]][start[0]] = 0
        self.grid[goal[1]][goal[0]] = 0

        # Pathfinding
        engine = PathfindingEngine(self.grid)
        algo_map = {
            "A* search": "astar",
            "Dijkstra": "dijkstra",
            "DFS": "dfs",
            "BFS": "bfs"
        }
        algo_name = algo_map.get(self.selected_algo, self.selected_algo.lower())

        #### 3amak osama ####
        # If manual controls are active (PlayerVsPlayer) we skip autonomous pathfinding
        # and allow the player to drive the agent manually.
        if self.manual_controls:
            # provide a minimal path fallback: start -> goal (not used for movement in manual mode)
            path = [start, goal]
        else:
            path = engine.find_path(start, goal, algo_name)
        #### 3amak osama ####
        
        if not path:
            print("No path could be found! Using direct line as fallback/debug.")
            path = [start, goal]

        # Agent Setup
        shape_colors = {
            "sphere_droid": (0.0, 1.0, 1.0),
            "robo_cube": (1.0, 0.3, 0.3),
            "mini_drone": (0.2, 0.7, 0.3),
            "crystal_alien": (0.8, 0.3, 1.0)
        }
        agent_color = shape_colors.get(self.selected_shape, (0.0, 1.0, 1.0))
        agent_speed = 2.5
        trail_length = 15
        
        self.agent = Agent(
            start, 
            goal, 
            path, 
            agent_speed, 
            agent_color, 
            self.selected_shape, 
            trail_length=trail_length
        )

        # Renderers Setup
        self.environment_renderer = EnvironmentRender3D(self.grid, cell_size=self.cell_size)
        self.agent_renderer = AgentRender(cell_size=self.cell_size, grid_size=self.grid_size)
        self.path_renderer = PathRender(
            cell_size=self.cell_size, 
            grid_size=self.grid_size, 
            ground_sampler=self.environment_renderer.get_ground_height
        )
        self.goal_renderer = GoalRender(cellSize=self.cell_size, grid_size=self.grid_size)
        
        # Camera
        self.camera = CameraController(distance=15, angle_x=45, angle_y=45)
        
        self.start_time = time.time()
        self.game_active = True
        return self.agent

    def _init_opengl(self):
        glClearColor(0.05, 0.05, 0.1, 1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glClearDepth(1.0)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 10.0, 5.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])

    def _setup_view(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, self.width / self.height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        pos = self.camera.calculate_camera_position()
        target = self.camera.target
        up = self.camera._calculate_up_vector()

        gluLookAt(pos[0], pos[1], pos[2],
                  target[0], target[1], target[2],
                  up[0], up[1], up[2])

    def update(self, dt):
        if not self.game_active:
            return

        # Camera Input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.camera.angle_x -= 60 * dt
        if keys[pygame.K_RIGHT]: self.camera.angle_x += 60 * dt
        if keys[pygame.K_UP]: self.camera.angle_y += 60 * dt
        if keys[pygame.K_DOWN]: self.camera.angle_y -= 60 * dt
        self.camera.angle_y = max(-89, min(89, self.camera.angle_y))

        #### 3amak osama ####
        # If manual controls are enabled, allow the player to move the agent with WASD.
        if self.manual_controls:
            # movement in world units per second (scaled by dt)
            speed = 5.0 * dt
            dx = 0.0
            dz = 0.0
            if keys[pygame.K_w]: dz -= speed
            if keys[pygame.K_s]: dz += speed
            if keys[pygame.K_a]: dx -= speed
            if keys[pygame.K_d]: dx += speed

            # try to mutate the agent.position in-place; if it's immutable, replace it
            try:
                # assume position is a mutable sequence like [x, y, z]
                self.agent.position[0] += dx
                self.agent.position[2] += dz
            except Exception:
                pos = list(self.agent.position)
                pos[0] += dx
                pos[2] += dz
                # store back as list (Agent should accept this; fallback if it expects tuple)
                self.agent.position = pos

            # Update agent renderer timing (so trails/visuals update)
            self.agent_renderer.update_time(dt)

            # check for manual goal reach (compare grid coords)
            try:
                curr_x = int(round(self.agent.position[0]))
                curr_z = int(round(self.agent.position[2]))
            except Exception:
                # if it's a tuple or other, coerce to list first
                pos = list(self.agent.position)
                curr_x = int(round(pos[0]))
                curr_z = int(round(pos[2]))

            goal_x, goal_z = self.goal
            if curr_x == goal_x and curr_z == goal_z:
                if not getattr(self.agent, '_victory_printed', False):
                    print("Manual goal reached!! 🎉🔥")
                    self.agent._victory_printed = True
                    # mark arrived to stop further processing if other systems check it
                    try:
                        self.agent.arrived = True
                    except Exception:
                        pass

            # update camera target to follow player
            wx = (self.agent.position[0]) * self.cell_size
            wy = self.agent.position[1] if len(self.agent.position) > 1 else 0
            wz = (self.agent.position[2]) * self.cell_size
            self.camera.target = [wx, wy, wz]

            # skip autonomous update
            return
        #### 3amak osama ####

        # Agent Update (autonomous modes)
        self.agent.update(dt)
        self.agent_renderer.update_time(dt)

        # Update Camera Target
        wx = (self.agent.position[0]) * self.cell_size
        wy = self.agent.position[1]
        wz = (self.agent.position[2]) * self.cell_size
        self.camera.target = [wx, wy, wz]
        
        if self.agent.arrived:
            if not hasattr(self.agent, '_victory_printed'):
                print("Goal reached! Congratulations!")
                self.agent._victory_printed = True

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self._setup_view()

        elapsed_time = time.time() - self.start_time
        self.environment_renderer.draw(elapsed_time)
        
        glDisable(GL_LIGHTING)
        self.path_renderer.draw_path(self.agent)
        self.path_renderer.draw_history(self.agent)
        glEnable(GL_LIGHTING)
        
        if not self.agent.arrived:
            glDisable(GL_LIGHTING)
            self.goal_renderer.draw_goal(self.agent)
            glEnable(GL_LIGHTING)
        
        self.agent_renderer.draw_agent(self.agent, self.agent.shape_type)

    def cleanup(self):
        pass
