import os
import bpy
import subprocess
import json

from numpy import add

from .properties import OpenVideoTrackerCameraProperties , OpenVideoTrackerPointsProperties

def get_addon_preferences():
    """Get the addon preferences"""
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[__package__].preferences
    return addon_prefs

def create_working_directory(base_path, video_name):
    """Create a working directory for the video tracking process"""
    working_dir = os.path.join(base_path, "video_tracking", video_name)
    images_dir = os.path.join(working_dir, "images")
    sparse_dir = os.path.join(working_dir, "sparse")
    
    # Create directories if they don't exist
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(sparse_dir, exist_ok=True)
    
    return working_dir, images_dir, sparse_dir

def get_video_name(video_path):
    """Extract the video name from the video path"""
    basename = os.path.basename(video_path)
    name, _ = os.path.splitext(basename)
    return name

def validate_executable_path(path):
    """Validate that an executable path exists and is executable"""
    if not path:
        return False, "Path is empty"
    
    if not os.path.exists(path):
        return False, f"Path does not exist: {path}"
        
    if not os.path.isfile(path):
        return False, f"Path is not a file: {path}"
        
    return True, "Valid"

def validate_video_path(path):
    """Validate that a video path exists and has a valid extension"""
    if not path:
        return False, "Path is empty"
    
    if not os.path.exists(path):
        return False, f"Path does not exist: {path}"
        
    if not os.path.isfile(path):
        return False, f"Path is not a file: {path}"
        
    valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    _, ext = os.path.splitext(path.lower())
    
    if ext not in valid_extensions:
        return False, f"Invalid file extension: {ext}"
        
    return True, "Valid"

def get_ffprobe_path():
    """Get the path to ffprobe executable"""
    addon_prefs = get_addon_preferences()
    return addon_prefs.ffprobe_path


def get_video_info(video_path):
    """Extract video information using ffprobe"""
    ffprobe_path = get_ffprobe_path()
    
    if not os.path.exists(ffprobe_path):
        return None, f"ffprobe not found at: {ffprobe_path}"
    
    try:
        # Run ffprobe to get video stream information
        cmd = [
            ffprobe_path,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return None, f"ffprobe error: {result.stderr}"
        
        data = json.loads(result.stdout)
        
        # Extract video stream information
        video_stream = None
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "video":
                video_stream = stream
                break
        
        if not video_stream:
            return None, "No video stream found"
        
        # Extract information
        frame_rate = video_stream.get("r_frame_rate", "N/A")
        if frame_rate != "N/A":
            # Convert frame rate from fraction to float
            try:
                num, den = frame_rate.split('/')
                frame_rate = f"{float(num) / float(den):.1f} fps"
            except:
                frame_rate = f"{frame_rate} fps"
        
        width = video_stream.get("width", "N/A")
        height = video_stream.get("height", "N/A")
        resolution = f"{width}x{height}" if width != "N/A" and height != "N/A" else "N/A"
        
        bitrate = video_stream.get("bit_rate", "N/A")
        if bitrate != "N/A":
            # Convert bitrate to Mbps
            try:
                bitrate_mbps = float(bitrate) / 1000000
                bitrate = f"{bitrate_mbps:.2f} Mbps"
            except:
                bitrate = f"{bitrate} bps"
        
        return {
            "frame_rate": frame_rate,
            "resolution": resolution,
            "bitrate": bitrate
        }, None
        
    except subprocess.TimeoutExpired:
        return None, "ffprobe timeout"
    except json.JSONDecodeError:
        return None, "Failed to parse ffprobe output"
    except Exception as e:
        return None, f"Error getting video info: {str(e)}"

def import_colmap_data(context , model_dir , image_dir):
    camera_prop:OpenVideoTrackerCameraProperties = context.scene.open_video_tracker.camera_importer
    point_prop:OpenVideoTrackerPointsProperties = context.scene.open_video_tracker.point_importer
    bpy.ops.import_scene.open_video_tracker_colmap(directory=model_dir,
    import_cameras=camera_prop.import_cameras,
    camera_extent=camera_prop.camera_extent,
    add_background_images=camera_prop.add_background_images,
    add_image_planes=camera_prop.add_image_planes,
    add_image_plane_emission=camera_prop.add_image_plane_emission,
    image_plane_transparency=camera_prop.image_plane_transparency,
    add_camera_motion_as_animation=camera_prop.add_camera_motion_as_animation,
    animation_frame_source=camera_prop.animation_frame_source, 
    add_animated_camera_background_images=camera_prop.add_animated_camera_background_images,
    number_interpolation_frames=camera_prop.number_interpolation_frames,
    consider_missing_cameras_during_animation=camera_prop.consider_missing_cameras_during_animation,
    interpolation_type=camera_prop.interpolation_type,
    remove_rotation_discontinuities=camera_prop.remove_rotation_discontinuities,
    adjust_render_settings=camera_prop.adjust_render_settings,
    image_dp = image_dir,
    import_points=point_prop.import_points,
    point_cloud_display_sparsity=point_prop.point_cloud_display_sparsity,
    center_points=point_prop.center_points,
    draw_points_with_gpu=point_prop.draw_points_with_gpu,
    add_points_to_point_cloud_handle=point_prop.add_points_to_point_cloud_handle,
    point_size=point_prop.point_size,
    add_points_as_mesh_oject=point_prop.add_points_as_mesh_oject,
    add_mesh_to_point_geometry_nodes=point_prop.add_mesh_to_point_geometry_nodes,
    point_radius=point_prop.point_radius,
    point_subdivisions=point_prop.point_subdivisions,
    add_color_as_custom_property=point_prop.add_color_as_custom_property
                                                                   )