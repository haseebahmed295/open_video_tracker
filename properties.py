import bpy
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty

def register():
    bpy.types.Scene.open_video_tracker = bpy.props.PointerProperty(type=OpenVideoTrackerProperties)

def unregister():
    del bpy.types.Scene.open_video_tracker

class OpenVideoTrackerProperties(bpy.types.PropertyGroup):
    # Video file path
    video_path: StringProperty(
        name="Video Path",
        description="Path to the input video file",
        default="",
        subtype='FILE_PATH'
    )
    
    # Frame extraction settings
    frame_rate: FloatProperty(
        name="Frame Rate",
        description="Frames per second to extract",
        default=2.0,
        min=0.1,
        max=30.0
    )
    
    quality: IntProperty(
        name="Quality",
        description="Quality factor for frame extraction (1=highest, 31=lowest)",
        default=1,
        min=1,
        max=31
    )
    
    # COLMAP feature extraction settings
    max_image_size: IntProperty(
        name="Max Image Size",
        description="Maximum image size for feature extraction (in pixels)",
        default=2000,
        min=100
    )
    
    use_gpu: BoolProperty(
        name="Use GPU",
        description="Use GPU for feature extraction",
        default=True
    )
    
    # COLMAP sequential matching settings
    overlap: IntProperty(
        name="Overlap",
        description="Number of overlapping images for sequential matching",
        default=10,
        min=1
    )
    
    # Progress indicator
    progress: IntProperty(
        name="Progress",
        description="Pipeline progress percentage",
        default=0,
        min=0,
        max=100
    )