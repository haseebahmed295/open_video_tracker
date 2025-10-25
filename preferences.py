import os
import bpy
from bpy.props import StringProperty, PointerProperty
from .utils import validate_cuda_version
def get_colmap_path():
    if validate_cuda_version():
        return os.path.join(os.path.dirname(__file__), "colmap","bin","colmap.exe")
    else:   
        return os.path.join(os.path.dirname(__file__), "colmap-nocuda","bin","colmap.exe")
class OpenVideoTrackerPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    colmap_path: StringProperty(
        name="COLMAP Path",
        description="Path to COLMAP executable",
        default=get_colmap_path(),
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
    use_gpu_features: bpy.props.BoolProperty(
        name="Use GPU in Feature Extraction",
        description="""Enable GPU acceleration for feature extraction
It is recommended to not diable this unless you face issues during feature extraction
Disabling this will cause usage of huge amounts of RAM""",
        default=True
    )
    use_gpu_matching: bpy.props.BoolProperty(
        name="Use GPU in Feature Matching",
        description="""Enable GPU acceleration for feature matching
Disable if pipelines crash during matching or show 'not enough gpu memory for matching' error""",
        default=validate_cuda_version()
    )
    use_gpu_reconstruction: bpy.props.BoolProperty(
        name="Use GPU in Sparse Reconstruction",
        description="""Enable GPU acceleration for sparse reconstruction
Disable if pipelines crash during reconstruction \n Not very importent unless you know what you are doing""",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text=f"Version: {'No CUDA' if not validate_cuda_version() else 'CUDA'}")
        row = layout.row()
        col = row.column(align=True)
        col.label(text="Use GPU In:")
        col.prop(self, "use_gpu_features", text="Feature Extraction" , toggle=True)
        col.prop(self, "use_gpu_matching", text="Feature Matching" , toggle=True)
        col.prop(self, "use_gpu_reconstruction", text="Sparse Reconstruction" , toggle=True)
        col = row.column(align=True)
        col.label(text="")
        
        header , panel = layout.panel("OPEN_VIDEO_TRACKER_PT_Panel" , default_closed=True)
        header.label(text="External Executables Paths")
        if panel:
            panel.prop(self, "colmap_path")
            panel.prop(self, "glomap_path")
            panel.prop(self, "ffmpeg_path")
            panel.prop(self, "ffprobe_path")