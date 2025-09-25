import bpy
from mathutils import Vector

def set_origin_to_lowest_vertex_multi():
    """For each selected mesh object, find the lowest vertex in world space
    and move the object's origin to that point."""
    ctx = bpy.context
    depsgraph = ctx.evaluated_depsgraph_get()
    sel_objs = [o for o in ctx.selected_objects if o.type == 'MESH']
    if not sel_objs:
        print("No mesh objects selected.")
        return

    # ensure object mode (origin_set requires object mode)
    if ctx.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # remember selection & active to restore later
    original_selection = list(sel_objs)
    original_active = ctx.view_layer.objects.active

    for obj in sel_objs:
        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.to_mesh()  # evaluated mesh (modifiers applied)

        if not mesh or len(mesh.vertices) == 0:
            print(f"{obj.name}: no vertices found, skipping.")
            eval_obj.to_mesh_clear()
            continue

        # find lowest vertex in WORLD coordinates
        min_world_z = None
        min_world_co = None
        for v in mesh.vertices:
            world_co = obj.matrix_world @ v.co
            if (min_world_z is None) or (world_co.z < min_world_z):
                min_world_z = world_co.z
                min_world_co = world_co.copy()

        # clear evaluated mesh
        eval_obj.to_mesh_clear()

        if min_world_co is None:
            print(f"{obj.name}: couldn't determine lowest point, skipping.")
            continue

        # set proper selection/active for origin_set to work safely
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        ctx.view_layer.objects.active = obj

        # move cursor to the lowest point and set origin there
        ctx.scene.cursor.location = min_world_co
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

        print(f"{obj.name}: origin moved to {min_world_co}")

    # restore original selection & active object
    bpy.ops.object.select_all(action='DESELECT')
    for o in original_selection:
        if o.name in ctx.scene.objects:
            o.select_set(True)
    if original_active and original_active.name in ctx.scene.objects:
        ctx.view_layer.objects.active = original_active
    elif original_selection:
        ctx.view_layer.objects.active = original_selection[0]

# Run
set_origin_to_lowest_vertex_multi()
