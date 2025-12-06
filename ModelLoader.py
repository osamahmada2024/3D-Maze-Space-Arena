import os
import numpy as np
from OpenGL.GL import *
from PIL import Image
import pywavefront

class ModelLoader:
    def __init__(self):
        self.models = {}
        self.textures = {}
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        
    def load_model(self, model_name):
        """Load a 3D model from a file"""
        if model_name in self.models:
            return self.models[model_name]
            
        model_path = os.path.join(self.base_path, 'models', f"{model_name}")
        
        if not os.path.exists(model_path):
            print(f"[WARNING] Model file not found: {model_path}")
            return None
            
        try:
            # Load the model using PyWavefront
            scene = pywavefront.Wavefront(
                model_path,
                create_materials=True,
                collect_faces=True
            )
            self.models[model_name] = scene
            print(f"[SUCCESS] Loaded model: {model_path}")
            return scene
            
        except Exception as e:
            print(f"[ERROR] Failed to load model {model_name}: {str(e)}")
            return None
    
    def load_texture(self, texture_path):
        """Load a texture from an image file"""
        if texture_path in self.textures:
            return self.textures[texture_path]
            
        full_path = os.path.join(self.base_path, 'models', texture_path)
        
        if not os.path.exists(full_path):
            print(f"[WARNING] Texture file not found: {full_path}")
            return None
            
        try:
            # Load image and convert to RGBA if needed
            image = Image.open(full_path)
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
                
            # Get image data
            img_data = np.array(list(image.getdata()), np.uint8)
            
            # Generate texture ID
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            
            # Set texture parameters
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            
            # Upload texture data
            glTexImage2D(
                GL_TEXTURE_2D, 0, GL_RGBA, 
                image.width, image.height,
                0, GL_RGBA, GL_UNSIGNED_BYTE, img_data
            )
            glGenerateMipmap(GL_TEXTURE_2D)
            
            self.textures[texture_path] = texture_id
            print(f"[SUCCESS] Loaded texture: {texture_path}")
            return texture_id
            
        except Exception as e:
            print(f"[ERROR] Failed to load texture {texture_path}: {str(e)}")
            return None
    
    def render_model(self, model_name, position=(0, 0, 0), scale=1.0, rotation=(0, 0, 0)):
        """Render a 3D model at the specified position and scale"""
        if model_name not in self.models:
            if not self.load_model(model_name):
                return
                
        model = self.models[model_name]
        
        glPushMatrix()
        glTranslatef(*position)
        glScalef(scale, scale, scale)
        
        # Apply rotation if specified (degrees)
        if rotation[0] != 0:
            glRotatef(rotation[0], 1, 0, 0)  # X rotation
        if rotation[1] != 0:
            glRotatef(rotation[1], 0, 1, 0)  # Y rotation
        if rotation[2] != 0:
            glRotatef(rotation[2], 0, 0, 1)  # Z rotation
        
        for mesh in model.mesh_list:
            # Bind texture if available
            if mesh.materials[0].texture is not None:
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, mesh.materials[0].texture.texture_id)
            else:
                glDisable(GL_TEXTURE_2D)
                
            # Draw the mesh
            glBegin(GL_TRIANGLES)
            for face in mesh.faces:
                for vertex_i in face:
                    if vertex_i < len(mesh.vertices):
                        glVertex3f(*mesh.vertices[vertex_i])
            glEnd()
            
        glPopMatrix()
        
    def cleanup(self):
        """Clean up resources"""
        for texture_id in self.textures.values():
            glDeleteTextures([texture_id])
        self.textures.clear()
        self.models.clear()

# Global instance
model_loader = ModelLoader()
