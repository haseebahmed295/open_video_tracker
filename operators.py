from threading import Thread
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty
import os
import subprocess
import shutil
from .utils import get_addon_preferences, create_working_directory, get_video_name, validate_executable_path, validate_video_path

class OPEN_VIDEO_TRACKER_OT_select_video(bpy.types.Operator, ImportHelper):
    """Select a video file"""
    bl_idname = "open_video_tracker.select_video"
    bl_label = "Select Video"
    
    filter_glob: StringProperty(
        default="*.mp4;*.avi;*.mov;*.mkv;*.wmv;*.flv;*.webm",
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        # Set the video path property
        context.scene.open_video_tracker.video_path = self.filepath
        return {'FINISHED'}


class OPEN_VIDEO_TRACKER_OT_run_pipeline_modal(bpy.types.Operator):
    """Modal operator for running the photogrammetry pipeline"""
    bl_idname = "open_video_tracker.run_pipeline_modal"
    bl_label = "Run Pipeline Modal"
    
    _timer = None
    _process = None
    _current_step = 0
    _total_steps = 7  # Frame extraction, feature extraction, matching, reconstruction, 2x export, cleanup
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_step = 0
        self._process = None
        
    def modal(self, context, event):
        if event.type == 'TIMER':            
            # Process is running, check if it's done
            if self._process is not None:
                if self._process.poll() is not None:
                    # Process finished
                    if self._process.returncode != 0:
                        # Try to get error output
                        try:
                            stdout, stderr = self._process.communicate(timeout=5)
                            error_msg = stderr.decode('utf-8') if stderr else f"Process failed with return code {self._process.returncode}"
                        except subprocess.TimeoutExpired:
                            error_msg = f"Process failed with return code {self._process.returncode} (timeout reading output)"
                        except Exception:
                            error_msg = f"Process failed with return code {self._process.returncode}"
                        
                        self.report({'ERROR'}, f"Process failed: {error_msg}")
                        self.cancel(context)
                        return {'CANCELLED'}
                    else:
                        self._process = None
                        self._current_step += 1
                        self.processs(context)
            
            # Check if we're done
            if self._current_step >= self._total_steps:
                self.report({'INFO'}, "Pipeline execution completed successfully")
                self.cancel(context)
                return {'FINISHED'}
                
        return {'PASS_THROUGH'}
        
    def execute(self, context):
        # Reset progress

        blend_path = bpy.data.filepath
        if not blend_path:
            self.report({'ERROR'}, "Blend file not found")
            return {'CANCELLED'}
        self.blend_dir = os.path.dirname(blend_path)
        
        # Start timer
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.5, window=context.window)
        wm.modal_handler_add(self)
        
        # Start first step
        self._thread = Thread(target=self.processs, args=(context,))
        self._thread.start()

        self.report({"INFO"} , "Processing... 😎")
        self._timer = context.window_manager.event_timer_add(0.01, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
        
    def processs(self, context):
        """Execute the next step in the pipeline"""
        props = context.scene.open_video_tracker
        prefs = get_addon_preferences()
        
        # Validate inputs
        is_valid, msg = validate_video_path(props.video_path)
        if not is_valid:
            self.report({'ERROR'}, f"Invalid video file: {msg}")
            self.cancel(context)
            return {'CANCELLED'}
            
        # Validate executable paths
        ffmpeg_valid, ffmpeg_msg = validate_executable_path(prefs.ffmpeg_path)
        colmap_valid, colmap_msg = validate_executable_path(prefs.colmap_path)
        glomap_valid, glomap_msg = validate_executable_path(prefs.glomap_path)
        
        if not ffmpeg_valid:
            self.report({'ERROR'}, f"Invalid FFmpeg path: {ffmpeg_msg}")
            self.cancel(context)
            return {'CANCELLED'}
            
        if not colmap_valid:
            self.report({'ERROR'}, f"Invalid COLMAP path: {colmap_msg}")
            self.cancel(context)
            return {'CANCELLED'}
            
        if not glomap_valid:
            self.report({'ERROR'}, f"Invalid GLOMAP path: {glomap_msg}")
            self.cancel(context)
            return {'CANCELLED'}
            
        # Get paths
        blend_dir = self.blend_dir
        video_name = get_video_name(props.video_path)
        
        # Create working directory structure
        working_dir, images_dir, sparse_dir = create_working_directory(blend_dir, video_name)
        database_path = os.path.join(working_dir, "database.db")
        model_dir = os.path.join(sparse_dir, "0")
        
        try:
            # Step 1: Frame extraction using FFmpeg
            self.report({'INFO'}, "Step 1/7: Extracting frames...")
            self._current_step = 1
            cmd = [
                prefs.ffmpeg_path,
                "-loglevel", "error",
                "-stats",
                "-i", props.video_path,
                "-qscale:v", str(props.quality),
                os.path.join(images_dir, "frame_%06d.jpg")
            ]
            self._process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
        
            # Step 2: COLMAP feature extraction
            self.report({'INFO'}, "Step 2/7: Extracting features...")
            self._current_step = 2
            cmd = [
                prefs.colmap_path,
                "feature_extractor",
                "--database_path", database_path,
                "--image_path", images_dir,
                "--ImageReader.single_camera", "1",
                "--SiftExtraction.use_gpu", "1" if props.use_gpu else "0",
                "--SiftExtraction.max_image_size", str(props.max_image_size)
            ]
            self._process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
        
            # Step 3: COLMAP sequential matching
            self.report({'INFO'}, "Step 3/7: Matching features...")
            self._current_step = 3
            cmd = [
                prefs.colmap_path,
                "sequential_matcher",
                "--database_path", database_path,
                "--SequentialMatching.overlap", str(props.overlap)
            ]
            self._process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
        
            # Step 4: GLOMAP sparse reconstruction
            self.report({'INFO'}, "Step 4/7: Running sparse reconstruction...")
            self._current_step = 4
            cmd = [
                prefs.glomap_path,
                "mapper",
                "--database_path", database_path,
                "--image_path", images_dir,
                "--output_path", sparse_dir
            ]
            self._process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
        
            # Step 5: Export TXT inside the model folder
            self.report({'INFO'}, "Step 5/7: Exporting model (internal)...")
            self._current_step = 5
            if os.path.exists(model_dir):
                cmd = [
                    prefs.colmap_path,
                    "model_converter",
                    "--input_path", model_dir,
                    "--output_path", model_dir,
                    "--output_type", "TXT"
                ]
                self._process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                # Skip if model doesn't exist
                self._current_step += 1
                self.processs(context)
                
        
            # Step 6: Export TXT to parent sparse directory
            self.report({'INFO'}, "Step 6/7: Exporting model (external)...")
            self._current_step = 6
            if os.path.exists(model_dir):
                cmd = [
                    prefs.colmap_path,
                    "model_converter",
                    "--input_path", model_dir,
                    "--output_path", sparse_dir,
                    "--output_type", "TXT"
                ]
                self._process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                # Skip if model doesn't exist
                self._current_step += 1
                self.processs(context)
                
        
            # Step 7: Cleanup and finish
            self.report({'INFO'}, "Step 7/7: Finalizing...")
            # This step is just for progress tracking
            self._current_step += 1
                
        except Exception as e:
            self.report({'ERROR'}, f"Failed to execute step: {str(e)}")
            self.cancel(context)
            return {'CANCELLED'}
            
    def cancel(self, context):
        # Clean up timer
        wm = context.window_manager
        if self._timer:
            wm.event_timer_remove(self._timer)
            
        # Terminate process if running
        if self._process and self._process.poll() is None:
            try:
                self._process.terminate()
                self._process.wait(timeout=5)  # Wait for termination
            except subprocess.TimeoutExpired:
                self._process.kill()  # Force kill if it doesn't terminate
            except Exception:
                pass  # Ignore errors during termination
            
        # Reset progress
        context.scene.open_video_tracker.progress = 0