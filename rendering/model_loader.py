"""
Fixed Model Loader with better error handling
"""

import os
import sys
import json
import struct
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


class SimpleGLTFModel:
    """Simple GLTF model loader that extracts mesh data from GLTF/GLB files"""
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.normals = []
        self.textures = []
        self.texture_id = None
        self.texture_uris = []  # Track texture URIs
        self.binary_data = None  # Store binary data for embedded textures
        self.gltf_dir = None  # Store directory for relative paths
        
    def load_from_file(self, gltf_path):
        """Load GLTF or GLB file and extract mesh data with proper texture support"""
        try:
            self.gltf_dir = os.path.dirname(os.path.abspath(gltf_path))
            gltf_data = None
            
            # Check if it's a GLB file (binary)
            if gltf_path.endswith('.glb'):
                gltf_data = self._load_glb(gltf_path)
            else:
                # Load as text GLTF
                with open(gltf_path, 'r') as f:
                    gltf_data = json.load(f)
            
            if not gltf_data:
                return False
            
            # Load all textures first (both external and embedded)
            if 'images' in gltf_data:
                for img_idx, image_data in enumerate(gltf_data['images']):
                    texture_id = None
                    
                    if 'uri' in image_data:
                        # External file reference
                        uri = image_data['uri']
                        self.texture_uris.append(uri)
                        
                        # Skip data: URIs and only load file paths
                        if not uri.startswith('data:'):
                            texture_path = os.path.join(self.gltf_dir, uri)
                            if os.path.exists(texture_path):
                                texture_id = self._load_texture(texture_path)
                                if texture_id:
                                    self.textures.append(texture_id)
                                    print(f"[SUCCESS] Loaded texture {img_idx}: {uri}")
                    
                    elif 'bufferView' in image_data:
                        # Embedded in GLB binary chunk
                        try:
                            texture_id = self._load_embedded_texture(gltf_data, image_data)
                            if texture_id:
                                self.textures.append(texture_id)
                                print(f"[SUCCESS] Loaded embedded texture {img_idx}")
                        except Exception as e:
                            print(f"[WARNING] Failed to load embedded texture {img_idx}: {str(e)}")
                    
                    if not texture_id:
                        self.textures.append(None)
            
            # Use first available texture
            if self.textures and self.textures[0]:
                self.texture_id = self.textures[0]
            
            # Extract mesh data (positions, normals, texcoords, indices)
            # We handle the first mesh and its first primitive for simplicity
            if 'meshes' in gltf_data and len(gltf_data['meshes']) > 0:
                mesh = gltf_data['meshes'][0]
                if 'primitives' in mesh and len(mesh['primitives']) > 0:
                    prim = mesh['primitives'][0]

                    # Positions
                    if 'attributes' in prim and 'POSITION' in prim['attributes']:
                        pos_accessor_idx = prim['attributes']['POSITION']
                        positions = self._get_accessor_data(gltf_data, pos_accessor_idx, self.gltf_dir)
                        if positions:
                            # Ensure positions are stored as list of tuples
                            self.vertices = [tuple(p) if isinstance(p, (list, tuple)) else (p,) for p in positions]

                    # Normals
                    if 'attributes' in prim and 'NORMAL' in prim['attributes']:
                        norm_accessor_idx = prim['attributes']['NORMAL']
                        normals = self._get_accessor_data(gltf_data, norm_accessor_idx, self.gltf_dir)
                        if normals:
                            self.normals = [tuple(n) if isinstance(n, (list, tuple)) else (n,) for n in normals]

                    # Texture coordinates (TEXCOORD_0)
                    if 'attributes' in prim and 'TEXCOORD_0' in prim['attributes']:
                        uv_accessor_idx = prim['attributes']['TEXCOORD_0']
                        uvs = self._get_accessor_data(gltf_data, uv_accessor_idx, self.gltf_dir)
                        if uvs:
                            self.textures = [tuple(uv) if isinstance(uv, (list, tuple)) else (uv,) for uv in uvs]

                    # Indices
                    if 'indices' in prim:
                        indices_accessor_idx = prim['indices']
                        indices = self._get_accessor_data(gltf_data, indices_accessor_idx, self.gltf_dir)
                        if indices:
                            # Convert flat index list to triangles
                            for i in range(0, len(indices), 3):
                                if i + 2 < len(indices):
                                    self.faces.append([int(indices[i]), int(indices[i+1]), int(indices[i+2])])
            
            print(f"[SUCCESS] Loaded GLTF: {gltf_path} - Vertices: {len(self.vertices)}, Faces: {len(self.faces)}, Textures: {len(self.textures)}")
            
            # Debug: Print vertex bounds
            if self.vertices:
                vertex_list = [v for v in self.vertices if isinstance(v, (tuple, list))]
                if vertex_list:
                    x_coords = [v[0] for v in vertex_list]
                    y_coords = [v[1] for v in vertex_list]
                    z_coords = [v[2] for v in vertex_list]
                    print(f"[DEBUG] Vertex bounds - X: [{min(x_coords):.2f}, {max(x_coords):.2f}], Y: [{min(y_coords):.2f}, {max(y_coords):.2f}], Z: [{min(z_coords):.2f}, {max(z_coords):.2f}]")
            
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load GLTF {gltf_path}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _load_glb(self, glb_path):
        """Load GLB file (binary GLTF container) with embedded data support"""
        try:
            with open(glb_path, 'rb') as f:
                # Read GLB header
                magic = f.read(4)
                if magic != b'glTF':
                    raise ValueError("Invalid GLB file")
                
                version = struct.unpack('<I', f.read(4))[0]
                file_length = struct.unpack('<I', f.read(4))[0]
                
                # Read first chunk (JSON)
                chunk_length = struct.unpack('<I', f.read(4))[0]
                chunk_type = f.read(4)
                
                if chunk_type != b'JSON':
                    raise ValueError("Invalid GLB chunk type")
                
                json_data = f.read(chunk_length)
                gltf_data = json.loads(json_data.decode('utf-8'))
                
                # Read binary buffer chunk
                bin_chunk_length = struct.unpack('<I', f.read(4))[0]
                bin_chunk_type = f.read(4)
                
                if bin_chunk_type == b'BIN\x00':
                    # Store binary data for later use
                    self.binary_data = f.read(bin_chunk_length)
                    gltf_data['_binary_data'] = self.binary_data
                
                return gltf_data
        except Exception as e:
            print(f"[ERROR] Failed to load GLB {glb_path}: {str(e)}")
            return None
    
    def _load_embedded_texture(self, gltf_data, image_data):
        """Load texture embedded in GLB file binary chunk"""
        try:
            if '_binary_data' not in gltf_data:
                return None
            
            buffer_view_idx = image_data.get('bufferView')
            if buffer_view_idx is None:
                return None
            
            buffer_view = gltf_data.get('bufferViews', [{}])[buffer_view_idx]
            byte_offset = buffer_view.get('byteOffset', 0)
            byte_length = buffer_view.get('byteLength', 0)
            
            binary_data = gltf_data['_binary_data']
            image_bytes = binary_data[byte_offset:byte_offset + byte_length]
            
            if not image_bytes:
                return None
            
            # Save temp image file and load
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                tmp.write(image_bytes)
                tmp_path = tmp.name
            
            texture_id = self._load_texture(tmp_path)
            try:
                os.unlink(tmp_path)
            except:
                pass
            return texture_id
        except Exception as e:
            print(f"[WARNING] Could not load embedded texture: {str(e)}")
            return None
    
    def _get_accessor_data(self, gltf_data, accessor_idx, base_dir):
        """Extract data from a GLTF accessor"""
        try:
            if accessor_idx >= len(gltf_data.get('accessors', [])):
                return None
            
            accessor = gltf_data['accessors'][accessor_idx]
            buffer_view_idx = accessor.get('bufferView')
            
            if buffer_view_idx is None:
                return None
            
            buffer_view = gltf_data['bufferViews'][buffer_view_idx]
            buffer_idx = buffer_view.get('buffer', 0)
            byte_offset = buffer_view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
            byte_stride = buffer_view.get('byteStride', 0)
            
            count = accessor.get('count', 0)
            component_type = accessor.get('componentType', 5126)  # FLOAT
            atype = accessor.get('type', 'SCALAR')
            
            # Determine size and format
            if atype == 'VEC3':
                num_components = 3
            elif atype == 'VEC2':
                num_components = 2
            elif atype == 'SCALAR':
                num_components = 1
            else:
                num_components = 3
            
            # Get buffer data - check if it's from GLB or external file
            buffer_data = None
            if '_binary_data' in gltf_data:
                # Use binary data from GLB file
                buffer_data = gltf_data['_binary_data'][byte_offset:byte_offset + (count * num_components * 4)]
            elif '_glb_file' in gltf_data:
                # Fallback: Read from GLB file
                glb_offset = gltf_data.get('_glb_buffer_offset', 0)
                with open(gltf_data['_glb_file'], 'rb') as f:
                    f.seek(glb_offset + byte_offset)
                    # Estimate needed bytes
                    if component_type == 5126:  # FLOAT
                        needed_bytes = count * num_components * 4
                    elif component_type in [5125, 5123]:  # UNSIGNED_INT or UNSIGNED_SHORT
                        needed_bytes = count * num_components * 4
                    else:
                        needed_bytes = count * num_components * 4
                    buffer_data = f.read(needed_bytes)
            else:
                # Read from external buffer file
                buffer_uri = gltf_data['buffers'][buffer_idx].get('uri')
                if not buffer_uri:
                    return None
                
                buffer_path = os.path.join(base_dir, buffer_uri)
                if not os.path.exists(buffer_path):
                    return None
                
                with open(buffer_path, 'rb') as f:
                    f.seek(byte_offset)
                    if component_type == 5126:
                        needed_bytes = count * num_components * 4
                    else:
                        needed_bytes = count * num_components * 4
                    buffer_data = f.read(needed_bytes)
            
            if not buffer_data:
                return None
            
            data = []
            offset = 0
            
            for i in range(count):
                values = []
                for c in range(num_components):
                    if component_type == 5126:  # FLOAT
                        if offset + 4 <= len(buffer_data):
                            val = struct.unpack('f', buffer_data[offset:offset+4])[0]
                            offset += 4
                        else:
                            val = 0.0
                    elif component_type == 5125:  # UNSIGNED_INT
                        if offset + 4 <= len(buffer_data):
                            val = struct.unpack('I', buffer_data[offset:offset+4])[0]
                            offset += 4
                        else:
                            val = 0
                    elif component_type == 5123:  # UNSIGNED_SHORT
                        if offset + 2 <= len(buffer_data):
                            val = struct.unpack('H', buffer_data[offset:offset+2])[0]
                            offset += 2
                        else:
                            val = 0
                    else:
                        val = 0
                    values.append(val)
                
                if len(values) == 1:
                    data.append(values[0])
                else:
                    data.append(tuple(values))
            
            return data
        except Exception as e:
            print(f"[WARNING] Error reading accessor: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _load_texture(self, texture_path):
        """Load a texture file"""
        if not PIL_AVAILABLE:
            return None
        
        try:
            image = Image.open(texture_path)
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
            
            return texture_id
        except Exception as e:
            print(f"[ERROR] Failed to load texture {texture_path}: {str(e)}")
            return None
    
    def render(self, scale=1.0, color=(1, 1, 1)):
        """Render the model with texture support"""
        if not self.vertices or not self.faces:
            return
        # Use texture (if available) and per-vertex normals/texcoords when present
        use_texture = (self.texture_id is not None)
        has_normals = bool(self.normals)
        has_texcoords = bool(self.textures)

        if use_texture:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            # Prefer showing the texture directly for the floor
            glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        else:
            glColor3f(*color)

        # If normals are present and lighting is enabled, ensure normals are normalized
        if has_normals:
            glEnable(GL_NORMALIZE)

        glBegin(GL_TRIANGLES)
        for face in self.faces:
            # face can be a list of indices (triangle) or polygon-fan; assume triangles
            for idx in face:
                if not (isinstance(idx, int) and 0 <= idx < len(self.vertices)):
                    continue

                # Apply normal if available
                if has_normals and idx < len(self.normals):
                    n = self.normals[idx]
                    if isinstance(n, (tuple, list)) and len(n) >= 3:
                        glNormal3f(float(n[0]), float(n[1]), float(n[2]))

                # Apply texcoord if available
                if use_texture and has_texcoords and idx < len(self.textures):
                    uv = self.textures[idx]
                    if isinstance(uv, (tuple, list)) and len(uv) >= 2:
                        glTexCoord2f(float(uv[0]), float(uv[1]))

                v = self.vertices[idx]
                if isinstance(v, (tuple, list)) and len(v) >= 3:
                    glVertex3f(v[0] * scale, v[1] * scale, v[2] * scale)
        glEnd()

        if use_texture:
            glDisable(GL_TEXTURE_2D)
        if has_normals:
            glDisable(GL_NORMALIZE)


class SimpleOBJModel:
    """Simple OBJ model loader that parses OBJ files directly"""
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.normals = []
        self.mtl_name = None
        
    def load_from_file(self, obj_path):
        """Load OBJ file with custom parsing that skips unsupported statements"""
        try:
            with open(obj_path, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse vertices
                if line.startswith('v '):
                    parts = line.split()
                    if len(parts) >= 4:
                        self.vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
                
                # Parse normals
                elif line.startswith('vn '):
                    parts = line.split()
                    if len(parts) >= 4:
                        self.normals.append((float(parts[1]), float(parts[2]), float(parts[3])))
                
                # Parse faces
                elif line.startswith('f '):
                    parts = line.split()[1:]
                    face = []
                    for part in parts:
                        # Handle vertex indices (v, v//vn, v/vt, v/vt/vn)
                        indices = part.split('/')
                        v_idx = int(indices[0]) - 1  # OBJ uses 1-based indexing
                        face.append(v_idx)
                    if len(face) >= 3:
                        self.faces.append(face)
                
                # Parse material
                elif line.startswith('usemtl '):
                    self.mtl_name = line.split()[1]
                
                # Skip unsupported statements (Tf, Pr, Pds, Pl, etc.)
                elif any(line.startswith(x) for x in ['Tf ', 'Pr ', 'Pds ', 'Pl ', 'Ke ', 'illum ']):
                    continue
            
            print(f"[SUCCESS] Loaded OBJ: {obj_path} - Vertices: {len(self.vertices)}, Faces: {len(self.faces)}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load OBJ {obj_path}: {str(e)}")
            return False
    
    def render(self, scale=1.0, color=(1, 1, 1)):
        """Render the model"""
        if not self.vertices or not self.faces:
            return
        
        glPushMatrix()
        glScalef(scale, scale, scale)
        glColor3f(*color)
        
        glBegin(GL_TRIANGLES)
        for face in self.faces:
            # Render each face as triangles
            for i in range(1, len(face) - 1):
                # Create triangles from polygons (fan triangulation)
                for idx in [face[0], face[i], face[i + 1]]:
                    if 0 <= idx < len(self.vertices):
                        v = self.vertices[idx]
                        glVertex3f(v[0], v[1], v[2])
        glEnd()
        
        glPopMatrix()


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
    """Load a 3D model using custom loaders (GLTF, OBJ, etc.)"""
    # Try GLTF loader first
    if model_path.endswith('.gltf'):
        gltf_model = SimpleGLTFModel()
        if gltf_model.load_from_file(model_path):
            return gltf_model
    
    # Try custom OBJ loader
    if model_path.endswith('.obj'):
        obj_model = SimpleOBJModel()
        if obj_model.load_from_file(model_path):
            return obj_model
    
    # Fall back to PyWavefront if available
    if not PYWF_AVAILABLE:
        print(f"[WARNING] PyWavefront not available, using fallback rendering for {model_path}")
        return None
    
    # Check if file exists
    if not os.path.exists(model_path):
        print(f"[WARNING] Model file not found: {model_path}")
        return None
    
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
        return None
        return None
    
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
        return None

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

def render_wavefront_model(wavefront_scene):
    """Render a PyWavefront scene"""
    if not wavefront_scene:
        return
    
    try:
        # Render all meshes in the scene
        if hasattr(wavefront_scene, 'mesh_list'):
            for mesh in wavefront_scene.mesh_list:
                glBegin(GL_TRIANGLES)
                if hasattr(mesh, 'vertices') and hasattr(mesh, 'faces'):
                    for face in mesh.faces:
                        for vertex_idx in face:
                            if vertex_idx < len(mesh.vertices):
                                v = mesh.vertices[vertex_idx]
                                glVertex3f(v[0], v[1], v[2])
                glEnd()
        elif hasattr(wavefront_scene, 'vertices'):
            # Direct vertex rendering
            glBegin(GL_TRIANGLES)
            for vertex in wavefront_scene.vertices:
                glVertex3f(vertex[0], vertex[1], vertex[2])
            glEnd()
    except Exception as e:
        print(f"[ERROR] Failed to render wavefront model: {str(e)}")