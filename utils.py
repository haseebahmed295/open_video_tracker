import os
import bpy

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