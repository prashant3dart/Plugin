bl_info = {
    "name": "PC Tools",
    "author": "Prashant",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > PC Tools",
    "category": "Object"
}

import bpy
from mathutils import Vector


# ---------------- ALIGN TOOL ----------------

class OBJECT_OT_align_objects(bpy.types.Operator):
    bl_idname = "object.align_objects_axis"
    bl_label = "Align Objects Along Axis"
    bl_options = {'REGISTER', 'UNDO'}

    axis: bpy.props.EnumProperty(
        name="Axis",
        items=[('X', "X", ""), ('Y', "Y", ""), ('Z', "Z", "")],
        default='X'
    )

    spacing: bpy.props.FloatProperty(
        name="Spacing",
        default=2.0,
        min=0.0
    )

    def execute(self, context):
        objects = context.selected_objects
        objects.sort(key=lambda obj: obj.name)

        for i, obj in enumerate(objects):
            if self.axis == 'X':
                obj.location.x = i * self.spacing
            elif self.axis == 'Y':
                obj.location.y = i * self.spacing
            elif self.axis == 'Z':
                obj.location.z = i * self.spacing

        return {'FINISHED'}


# ---------------- PIVOT TOOL ----------------

class OBJECT_OT_pivot_center_bottom(bpy.types.Operator):
    bl_idname = "object.pivot_center_bottom"
    bl_label = "Pivot Center Bottom"

    def execute(self, context):

        ctx = context
        depsgraph = ctx.evaluated_depsgraph_get()

        sel_objs = [o for o in ctx.selected_objects if o.type == 'MESH']

        for obj in sel_objs:

            world_coords = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

            avg_x = sum(v.x for v in world_coords) / len(world_coords)
            avg_y = sum(v.y for v in world_coords) / len(world_coords)

            eval_obj = obj.evaluated_get(depsgraph)
            mesh = eval_obj.to_mesh()

            min_z = None

            for v in mesh.vertices:
                world_co = obj.matrix_world @ v.co

                if min_z is None or world_co.z < min_z:
                    min_z = world_co.z

            eval_obj.to_mesh_clear()

            new_origin = Vector((avg_x, avg_y, min_z))

            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            ctx.view_layer.objects.active = obj

            ctx.scene.cursor.location = new_origin
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        return {'FINISHED'}


# ---------------- UI PANEL ----------------

class OBJECT_PT_pc_tools_panel(bpy.types.Panel):
    bl_label = "PC Tools"
    bl_idname = "OBJECT_PT_pc_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PC Tools'

    def draw(self, context):
        layout = self.layout

        layout.label(text="Align Tool")
        layout.operator("object.align_objects_axis")

        layout.separator()

        layout.label(text="Pivot Tool")
        layout.operator("object.pivot_center_bottom")


# ---------------- REGISTER ----------------

classes = (
    OBJECT_OT_align_objects,
    OBJECT_OT_pivot_center_bottom,
    OBJECT_PT_pc_tools_panel,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()