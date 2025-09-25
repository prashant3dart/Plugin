import bpy
from mathutils import Vector

def set_origin_to_xy_center_only():
    """Move origin to the XY center of each selected mesh object,
    keeping the Z location unchanged."""
    ctx = bpy.context
    sel_objs = [o for o in ctx.selected_objects if o.type == 'MESH']
    if not sel_objs:
        print("No mesh objects selected.")
        return

    if ctx.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # remember original selection & active object
    original_selection = sel_objs[:]
    original_active = ctx.view_layer.objects.active

    for obj in sel_objs:
        # Get bounding box corners in world space
        world_coords = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

        # Find average X and Y (center), but keep object's current origin Z
        avg_x = sum(v.x for v in world_coords) / len(world_coords)
        avg_y = sum(v.y for v in world_coords) / len(world_coords)
        current_z = obj.location.z  # keep current origin Z

        new_origin = Vector((avg_x, avg_y, current_z))

        # Set cursor to new origin and update pivot
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        ctx.view_layer.objects.active = obj
        ctx.scene.cursor.location = new_origin
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

        print(f"{obj.name}: origin moved to XY center {avg_x:.3f}, {avg_y:.3f}, Z kept at {current_z:.3f}")

    # restore selection
    bpy.ops.object.select_all(action='DESELECT')
    for o in original_selection:
        if o.name in ctx.scene.objects:
            o.select_set(True)
    if original_active and original_active.name in ctx.scene.objects:
        ctx.view_layer.objects.active = original_active
    elif original_selection:
        ctx.view_layer.objects.active = original_selection[0]


# Run
set_origin_to_xy_center_only()
