import bpy

# Settings
axis = 'X'   # Choose 'X', 'Y', or 'Z'
spacing = 2  # Distance between objects

# Get selected objects
objects = bpy.context.selected_objects

# Sort by name (optional, keeps order consistent)
objects.sort(key=lambda obj: obj.name)

# Align objects
for i, obj in enumerate(objects):
    if axis == 'X':
        obj.location.x = i * spacing
    elif axis == 'Y':
        obj.location.y = i * spacing
    elif axis == 'Z':
        obj.location.z = i * spacing
