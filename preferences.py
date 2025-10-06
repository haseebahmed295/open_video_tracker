import bpy
from bpy.props import StringProperty, PointerProperty

class OpenVideoTrackerPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    colmap_path: StringProperty(
        name="COLMAP Path",
        description="Path to COLMAP executable",
        default="colmap/colmap.exe",
        subtype='FILE_PATH'
    )
    
    glomap_path: StringProperty(
        name="GLOMAP Path",
        description="Path to GLOMAP executable",
        default="glomap/glomap.exe",
        subtype='FILE_PATH'
    )
    
    ffmpeg_path: StringProperty(
        name="FFmpeg Path",
        description="Path to FFmpeg executable",
        default="ffmpeg.exe",
        subtype='FILE_PATH'
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "colmap_path")
        layout.prop(self, "glomap_path")
        layout.prop(self, "ffmpeg_path")