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

    camera_model: EnumProperty(
        name="Camera Model",
        description="Camera model for feature extraction",
        items=[
            ('SIMPLE_PINHOLE', "Simple Pinhole", "Simplest model: assumes a perfect pinhole camera (no distortion). Example: High-quality DSLR cameras with prime lenses", 1),
            ('PINHOLE', "Pinhole", "Like SIMPLE_PINHOLE, but allows for more parameters. Example: Professional cinema cameras", 2),
            ('SIMPLE_RADIAL', "Simple Radial", "Adds radial distortion (common in consumer cameras). Example: iPhone/Samsung smartphone cameras", 3),
            ('SIMPLE_RADIAL_FISHEYE', "Simple Radial Fisheye", "For fisheye lenses with radial distortion. Example: GoPro Hero action cameras", 4),
            ('RADIAL', "Radial", "More complex radial distortion model. Example: Mirrorless cameras with zoom lenses", 5),
            ('RADIAL_FISHEYE', "Radial Fisheye", "For fisheye lenses with more complex distortion. Example: Insta360 or Ricoh Theta 360° cameras", 6),
            ('OPENCV', "OpenCV", "Uses standard OpenCV distortion model (common in computer vision). Example: Webcam, security cameras", 7),
            ('OPENCV_FISHEYE', "OpenCV Fisheye", "OpenCV's model for fisheye lenses. Example: Wide-angle security cameras", 8),
            ('FULL_OPENCV', "Full OpenCV", "Full OpenCV model with all possible distortions. Example: Machine vision, robotics applications", 9),
            ('FOV', "FOV", "For wide-angle lenses. Example: DJI drone cameras, wide-angle photography", 10),
            ('THIN_PRISM_FISHEYE', "Thin Prism Fisheye", "For fisheye lenses with prism-like distortion. Example: Specialized scientific cameras", 11),
            ('RAD_TAN_THIN_PRISM_FISHEYE', "Radial Tangential Thin Prism Fisheye", "Combines radial, tangential, and thin prism for fisheye lenses. Example: Advanced robotics, VR camera systems", 12),
        ],
        default='SIMPLE_RADIAL',
    )

    # Advanced feature extraction settings
    max_num_features: IntProperty(
        name="Max Features",
        description="Maximum number of features to extract per image",
        default=8192,
        min=100,
        max=50000
    )

    # GLOMAP reconstruction settings
    max_num_tracks: IntProperty(
        name="Max Tracks",
        description="""Maximum number of tracks per image.
Typically, one image should not need more than 1000 tracks to achieve good performance.""",
        default=1000,
        min=100,
        max=100000
    )

    constraint_type: EnumProperty(
        name="Constraint Type",
        description="Type of constraints for GLOMAP reconstruction",
        items=[
            ('ONLY_POINTS', "Points Only", "Use only point constraints for reconstruction", 1),
            ('ONLY_CAMERAS', "Cameras Only", "Use only camera constraints for reconstruction", 2),
            ('POINTS_AND_CAMERAS_BALANCED', "Balanced", "Balanced point and camera constraints", 3),
            ('POINTS_AND_CAMERAS', "Points and Cameras", "Use both point and camera constraints", 4),
        ],
        default='POINTS_AND_CAMERAS_BALANCED',
    )
    
    # Additional GLOMAP options
    max_epipolar_error: IntProperty(
        name="Max Epipolar Error",
        description="Maximum epipolar error for relative pose estimation. Increase for high-resolution or blurry images (e.g., 4 or 10)",
        default=1,
        min=1,
        max=20
    )

    max_global_positioning_iterations: IntProperty(
        name="Max Global Positioning Iterations",
        description="Maximum number of iterations for global positioning",
        default=100,
        min=1,
        max=1000
    )
    
    max_bundle_adjustment_iterations: IntProperty(
        name="Max Bundle Adjustment Iterations",
        description="Maximum number of iterations for bundle adjustment",
        default=200,
        min=1,
        max=1000
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