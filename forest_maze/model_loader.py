"""
Fixed Model Loader with better error handling
"""

import os
import sys
from OpenGL.GL import *
from OpenGL.GLU import *

# Try to import required packages with better error handling
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("[WARNING] NumPy not available - some features may be limited")
    # Define a simple array type for basic functionality
    class SimpleArray:
        def __init__(self, data, dtype=None):
            self.data = data
            self.shape = (len(data),)
        def tolist(self):
            return self.data

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("[WARNING] PIL/Pillow not available - texture loading disabled")

try:
    import pywavefront
    PYWF_AVAILABLE = True
except ImportError:
    PYWF_AVAILABLE = False
    print("[WARNING] PyWavefront not available - 3D model loading disabled")

class SimpleModel:
    """Simple model class with basic rendering"""
    def __init__(self, position=(0, 0, 0), scale=1.0):
        self.position = position
        self.scale = scale
        self.vertices = []
        self.faces = []
        self.texture = None
        
    def render(self):
        """Basic rendering with fallback"""
        glPushMatrix()
        glTranslatef(*self.position)
        glScalef(self.scale, self.scale, self.scale)
        
        if self.vertices and self.faces:
            glBegin(GL_TRIANGLES)
            for face in self.faces:
                for vertex in face:
                    if vertex < len(self.vertices):
                        glVertex3f(*self.vertices[vertex])
            glEnd()
        else:
            # Fallback: Draw a simple cube
            self._draw_fallback_cube()
            
        glPopMatrix()
    
    def _draw_fallback_cube(self):
        """Draw a simple colored cube as fallback"""
        vertices = [
            # Front face
            [-0.5, -0.5,  0.5], [0.5, -0.5,  0.5], [0.5,  0.5,  0.5], [-0.5,  0.5,  0.5],
            # Back face
            [-0.5, -0.5, -0.5], [-0.5,  0.5, -0.5], [0.5,  0.5, -0.5], [0.5, -0.5, -0.5],
        ]
        
        faces = [
            (0, 1, 2, 3),  # Front
            (4, 5, 6, 7),  # Back
            (0, 3, 5, 4),  # Left
            (1, 7, 6, 2),  # Right
            (3, 2, 6, 5),  # Top
            (0, 4, 7, 1),  # Bottom
        ]
        
        glColor3f(0.5, 0.5, 0.5)  # Gray color
        for face in faces:
            glBegin(GL_QUADS)
            for vertex in face:
                glVertex3f(*vertices[vertex])
            glEnd()

def load_model(model_path, texture_path=None):
    """Load a 3D model with fallback to simple rendering"""
    if not PYWF_AVAILABLE:
        print(f"[WARNING] PyWavefront not available, using fallback rendering for {model_path}")
        return SimpleModel()
    
    try:
        scene = pywavefront.Wavefront(
            model_path,
            create_materials=True,
            collect_faces=True
        )
        print(f"[SUCCESS] Loaded model: {model_path}")
        return scene
    except Exception as e:
        print(f"[ERROR] Failed to load model {model_path}: {str(e)}")
        return SimpleModel()

def load_texture(image_path):
    """Load a texture with fallback"""
    if not PIL_AVAILABLE:
        print(f"[WARNING] PIL/Pillow not available, texture {image_path} not loaded")
        return None
        
    try:
        image = Image.open(image_path)
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
            
        img_data = image.tobytes()
        width, height = image.size
        
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                    GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)
        
        print(f"[SUCCESS] Loaded texture: {image_path}")
        return texture_id
        
    except Exception as e:
        print(f"[ERROR] Failed to load texture {image_path}: {str(e)}")
        return None