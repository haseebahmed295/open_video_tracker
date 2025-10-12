bl_info = {
    "name": "Open Video Tracker",
    "description": "Blender addon for video tracking using COLMAP and GLOMAP",
    "author": "Open Video Tracker Team",
    "version": (0, 1, 0),
    "blender": (2, 93, 0),
    "location": "3D View > Open Video Tracker",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "3D View"}

if "bpy" in locals():
    import importlib
    importlib.reload(ui)

import bpy
from . import ui, operators, properties, preferences
from .importer.importer import ImportColmapOperator
classes = (
    # Preferences
    preferences.OpenVideoTrackerPreferences,
    
    # Properties
    properties.OpenVideoTrackerProperties,
    
    # Operators
    operators.OPEN_VIDEO_TRACKER_OT_run_pipeline_modal,
    ImportColmapOperator,
    
    # UI Panels
    ui.OPEN_VIDEO_TRACKER_PT_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    properties.register()

def unregister():
    properties.unregister()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()