import bpy
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty, EnumProperty
import os

def update_video_path(self, context):
    """Update function called when video_path property changes"""
    if not self.video_path:
        # Clear video info if path is empty
        self.video_frame_rate = ""
        self.video_resolution = ""
        self.video_bitrate = ""
        return

    if not os.path.exists(self.video_path):
        # Clear video info if file doesn't exist
        self.video_frame_rate = "File not found"
        self.video_resolution = ""
        self.video_bitrate = ""
        return

    # Import here to avoid circular imports
    try:
        from .utils import get_video_info
        video_info, error = get_video_info(self.video_path)

        if video_info:
            self.video_frame_rate = video_info.get("frame_rate", "N/A")
            self.video_resolution = video_info.get("resolution", "N/A")
            self.video_bitrate = video_info.get("bitrate", "N/A")
        else:
            self.video_frame_rate = f"Error: {error}" if error else "N/A"
            self.video_resolution = "N/A"
            self.video_bitrate = "N/A"
    except Exception as e:
        self.video_frame_rate = f"Error: {str(e)}"
        self.video_resolution = "N/A"
        self.video_bitrate = "N/A"

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
        subtype='FILE_PATH',
        update=update_video_path
    )
    
    # Frame extraction settings
    frame_rate: IntProperty(
        name="Frame Rate",
        description="Frames per second to extract",
        default=30,
        min=1,
        max=120
    )
    
    quality: EnumProperty(
        name="Quality",
        description="Quality preset for frame extraction",
        items=[
            ('1', "Native", "Highest quality, largest file size", 1),
            ('2', "High", "Very high quality, large file size", 2),
            ('4', "Balanced", "High quality, good balance", 3),
            ('8', "Low", "Low quality, small file size", 4),
            ('16', "Lowest", "Lowest quality, smallest file size", 5),

        ],
        default='2',
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
    
    # Video information properties
    video_frame_rate: StringProperty(
        name="Video Frame Rate",
        description="Frame rate of the loaded video",
        default="",
    )
    
    video_resolution: StringProperty(
        name="Video Resolution",
        description="Resolution of the loaded video",
        default="",
    )
    
    video_bitrate: StringProperty(
        name="Video Bitrate",
        description="Bitrate of the loaded video",
        default="",
    )