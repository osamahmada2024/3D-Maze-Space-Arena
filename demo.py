import sys
import os

# Ensure we can import mazespace from current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mazespace import Renderer

def main():
    print("Initializing Mazespace Renderer...")
    renderer = Renderer(width=800, height=600)
    
    print("Adding shapes...")
    renderer.draw("drone", (0, 0, 0), color=(0, 1, 1))
    renderer.draw("cube", (5, 0, 5), color=(1, 0, 0))
    renderer.draw("sphere", (-5, 0, -5), color=(0, 1, 0))
    renderer.draw("crystal", (0, 2, 5), color=(0.8, 0, 0.8))
    
    # Normally we would call renderer.show() but since this is a headless automated test environment,
    # we will just print success. If we were local, we would call it.
    # renderer.show()
    print("Renderer initialized and objects added successfully.")
    
    # Verify internal state
    assert len(renderer.objects) == 4
    print("Verification passed: 4 objects in scene.")

if __name__ == "__main__":
    main()
