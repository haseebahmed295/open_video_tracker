import os
import bpy
from bpy.props import StringProperty, PointerProperty

class OpenVideoTrackerPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    colmap_path: StringProperty(
        name="COLMAP Path",
        description="Path to COLMAP executable",
        default=os.path.join(os.path.dirname(__file__), "colmap","bin","colmap.exe"),
        subtype='FILE_PATH'
    )
    
    glomap_path: StringProperty(
        name="GLOMAP Path",
        description="Path to GLOMAP executable",
        default=os.path.join(os.path.dirname(__file__), "glomap","bin","glomap.exe"),
        subtype='FILE_PATH'
    )
    
    ffmpeg_path: StringProperty(
        name="FFmpeg Path",
        description="Path to FFmpeg executable",
        default=os.path.join(os.path.dirname(__file__), "ffmpeg","bin","ffmpeg.exe"),
        subtype='FILE_PATH'
    )
    ffprobe_path: StringProperty(
        name="FFprobe Path",
        description="Path to FFprobe executable",
        default=os.path.join(os.path.dirname(__file__), "ffmpeg","bin","ffprobe.exe"),
        subtype='FILE_PATH'
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "colmap_path")
        layout.prop(self, "glomap_path")
        layout.prop(self, "ffmpeg_path")
        layout.prop(self, "ffprobe_path")