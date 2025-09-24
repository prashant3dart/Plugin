import bpy
import bmesh
import os
import re
import colorsys

# Folder where all atlases are stored
ATLAS_FOLDER = r"E:\Work\Dawrf\Dwarf atlas"

def get_atlas_files(folder):
    """Return a dict mapping {index:int -> filepath} from atlas filenames."""
    atlas_files = {}
    for f in os.listdir(folder):
        match = re.match(r"^(\d+)_.*\.(png|jpg|tif|tga)$", f, re.IGNORECASE)
        if match:
            index = int(match.group(1))  # e.g. "01" -> 1
            atlas_files[index] = os.path.join(folder, f)
    return atlas_files

def assign_materials_from_idmap(obj, atlas_files, num_stripes=16):
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    uv_layer = bm.loops.layers.uv.get("IDMap")
    if uv_layer is None:
        print(f"{obj.name} has no 'IDMap' UV layer")
        bm.free()
        return
    
    # Ensure material slots
    while len(obj.material_slots) < num_stripes:
        index = len(obj.material_slots) + 1
        mat = bpy.data.materials.new(name=f"Atlas_{index:02d}")
        mat.use_nodes = True

        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # Clear default nodes
        for n in nodes:
            nodes.remove(n)

        tex_node = nodes.new("ShaderNodeTexImage")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        output = nodes.new("ShaderNodeOutputMaterial")

        tex_node.location = (-400, 0)
        bsdf.location = (-200, 0)
        output.location = (0, 0)

        # Load texture if exists
        if index in atlas_files:
            tex_path = atlas_files[index]
            tex_node.image = bpy.data.images.load(tex_path, check_existing=True)
        else:
            print(f"⚠️ Missing atlas for index {index:02d}")

        # Link nodes
        links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

        # Assign viewport color
        hue = (index-1) / num_stripes
        r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
        mat.diffuse_color = (r, g, b, 1.0)

        obj.data.materials.append(mat)
    
    # Assign faces based on UV.x
    for face in bm.faces:
        uv = face.loops[0][uv_layer].uv
        stripe_index = int(uv.x * num_stripes)
        stripe_index = max(0, min(num_stripes - 1, stripe_index))
        face.material_index = stripe_index
    
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


# --- Run on selection ---
atlas_files = get_atlas_files(ATLAS_FOLDER)

for obj in bpy.context.selected_objects:
    if obj.type == 'MESH':
        assign_materials_from_idmap(obj, atlas_files, num_stripes=16)

print("✅ Atlas materials assigned using file name numbers")
