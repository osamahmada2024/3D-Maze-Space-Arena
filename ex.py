from mazespace import Renderer

print("Initializing Mazespace Renderer...")

# 1. Initialize the Renderer
r = Renderer(width=800, height=600, bg_color=(0.1, 0.1, 0.1, 1.0))

print("Adding shapes...")

# 2. Add shapes
# Center Drone
r.draw(shape="drone", position=(0, 0, 0), color=(0.0, 1.0, 1.0))

# Surrounding Objects
r.draw(shape="cube", position=(5, 0, 5), color=(1.0, 0.3, 0.3))
r.draw(shape="sphere", position=(-5, 2, -5), color=(0.5, 1.0, 0.5))
r.draw(shape="crystal", position=(0, 3, 6), color=(0.8, 0.0, 1.0))

print("Opening window... (Close window to exit)")

# 3. Show the Window (This blocks until the window is closed)
r.show()

print("Done!")
