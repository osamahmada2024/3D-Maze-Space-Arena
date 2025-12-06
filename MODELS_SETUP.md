# Models Folder Setup Guide

## Directory Structure

```
models/
├── tree.3ds                 (Your tree model)
├── tree.jpg                 (Tree texture - if separate from .3ds)
└── grass.3ds                (Your grass model)
```

## Model Files Expected

### 1. **tree.3ds**

- **Format:** Autodesk 3DS
- **Description:** 3D tree model with trunk and foliage
- **Texture:** Includes JPG texture embedded or as separate file
- **Placement:** `/models/tree.3ds`

**How to place:**

- Copy your tree.3ds file to the models folder
- If texture is separate (tree.jpg), also copy it to models folder
- The loader will automatically find and load the texture

### 2. **grass.3ds**

- **Format:** Autodesk 3DS
- **Description:** Grass/ground plane model
- **Placement:** `/models/grass.3ds`
- **Note:** Texture may be embedded in the file

**How to place:**

- Copy your grass.3ds file to the models folder

## How the Loader Works

The `model_loader.py` system will:

1. **Automatically detect** .3ds files in the `/models` folder
2. **Parse 3DS chunks** to extract:
   - Mesh vertices and faces
   - Texture coordinates
   - Material definitions
   - Texture filenames
3. **Load textures** from:
   - Filenames embedded in .3ds file
   - Same directory as .3ds file
   - `/models` directory
4. **Generate normals** for proper lighting
5. **Fall back to procedural** rendering if models fail to load

## File Naming Convention

Keep exactly these names:

- `tree.3ds` - for tree obstacles and environment objects
- `grass.3ds` - for floor/ground (currently renders as procedural, ready for model)

## What Happens Automatically

When the game starts:

1. ✅ Forest scene initializes
2. ✅ EnvironmentObjectManager loads models from `/models`
3. ✅ Trees use 3DS model if available, else procedural rendering
4. ✅ Console shows:
   - `[OK] Loaded tree model: models/tree.3ds`
   - `[OK] Loaded texture: models/tree.jpg`
   - Or fallback messages if files not found

## Texture Requirements

### For tree.jpg (if separate):

- Format: JPG, PNG, or other PIL-supported format
- Must be named same as texture reference in .3ds file
- Place in `/models` folder
- Recommended size: 512x512 or 1024x1024
- Should contain bark/wood texture for realistic appearance

### For grass.3ds texture:

- Check if texture is embedded in .3ds file
- If separate file needed, it will be specified in model metadata
- Place any separate textures in `/models` folder

## Troubleshooting

If models don't appear:

1. Check console for error messages
2. Verify file names are exact: `tree.3ds`, `grass.3ds`
3. Ensure files are in `/models` folder
4. Verify texture files exist and are readable
5. Check that PIL (Python Imaging Library) is installed

## Alternative: Use Procedural Rendering

If model loading has issues, the game automatically uses procedural rendering:

- **Trees:** Generated as brown cylinder + green sphere (always works)
- **Grass:** Rendered as green quad floor with grid overlay (always works)

This ensures the game always runs smoothly.

## Integration Points

Models are used in:

- `forest_maze/environment_objects.py` - Tree class render() method
- `forest_maze/forest_scene.py` - Wall rendering (trees for obstacles)
- Automatic fallback to procedural if models unavailable

## Next Steps

1. Place your tree.3ds file in the `/models` folder
2. If texture is separate, place tree.jpg in `/models` folder
3. Place your grass.3ds file in the `/models` folder
4. Run the game and check console for load confirmation
5. If issues occur, check error messages and verify file names
