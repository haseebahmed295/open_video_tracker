from threading import Thread
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty
import os
import subprocess
import shutil

from .properties import OpenVideoTrackerProperties
from .utils import get_addon_preferences, create_working_directory, get_video_name, validate_executable_path, validate_video_path



class OPEN_VIDEO_TRACKER_OT_run_pipeline_modal(bpy.types.Operator):
    """Modal operator for running the photogrammetry pipeline"""
    bl_idname = "open_video_tracker.run_pipeline_modal"
    bl_label = "Run Pipeline Modal"
    
    _timer = None
    _process = None
    _current_step = 0

    is_active = False
    _message = ""
    
    @property
    def current_step(self):
        # Access the current step from the thread
        return self._current_step
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_step = 0
        self._process = None
        self._prev = None
        
    def update_current_step(self, step):
        # Thread-safe update of current step
        self._current_step = step
        
    def modal(self, context, event):
        if event.type == 'TIMER':
            context.scene.open_video_tracker.progress = self.current_step
            
            # Check if thread is still alive
            if self._thread and not self._thread.is_alive():
                # Thread has finished
                self.report({'INFO'}, "Pipeline execution completed")
                self.cancel(context)
                return {'FINISHED'}
                
        return {'PASS_THROUGH'}
        
    def execute(self, context):
        # Reset progress

        blend_path = bpy.data.filepath
        if not blend_path:
            self.report({'ERROR'}, "Blend file is not saved")
            return {'CANCELLED'}
        self.blend_dir = os.path.dirname(blend_path)
        OPEN_VIDEO_TRACKER_OT_run_pipeline_modal.is_active = True
        
        # Start first step
        self._thread = Thread(target=self.processs, args=(context,))
        self._thread.daemon = True  # Dies when main thread dies
        self._thread.start()

        self.report({"INFO"} , "Processing... 😎")
        self._timer = context.window_manager.event_timer_add(0.05, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
        
    def processs(self, context):
        """Execute the next step in the pipeline"""
        props:OpenVideoTrackerProperties = context.scene.open_video_tracker
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
        
        # Step 1: Frame extraction using FFmpeg
        self.report({'INFO'}, "Step 1/7: Extracting frames...")
        self.update_current_step(1)
        OPEN_VIDEO_TRACKER_OT_run_pipeline_modal._message = "Step 1/7: Extracting frames..."
        print("Step 1/7: Extracting frames...")
        cmd = [
            prefs.ffmpeg_path,
            "-loglevel", "error",
            "-stats",
            "-i", props.video_path,
            "-qscale:v", str(props.quality),
            "-r" , str(props.frame_rate),
            os.path.join(images_dir, "frame_%06d.jpg")
        ]
        self._process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        self.print_logs(self._process)
        if self._process.returncode != 0:
            self.report({'ERROR'}, "Frame extraction failed")
            return  # Early exit from the thread function
    
        # Step 2: COLMAP feature extraction
        self.report({'INFO'}, "Step 2/7: Extracting features...")
        self.update_current_step(2)
        print("Step 2/7: Extracting features...")
        OPEN_VIDEO_TRACKER_OT_run_pipeline_modal._message = "Step 2/7: Extracting features..."
        cmd = [
            prefs.colmap_path,
            "feature_extractor",
            "--database_path", database_path,
            "--image_path", images_dir,
            "--ImageReader.single_camera", "1",
            "--SiftExtraction.use_gpu", "1" if props.use_gpu else "0",
            "--SiftExtraction.max_image_size", str(props.max_image_size)
        ]
        self._process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        self.print_logs(self._process)
        if self._process.returncode != 0:
            self.report({'ERROR'}, "Feature extraction failed")
            return  # Early exit from the thread function

    
        # Step 3: COLMAP sequential matching
        self.report({'INFO'}, "Step 3/7: Matching features...")
        self.update_current_step(3)
        print("Step 3/7: Matching features...")
        OPEN_VIDEO_TRACKER_OT_run_pipeline_modal._message = "Step 3/7: Matching features..."

        cmd = [
            prefs.colmap_path,
            "sequential_matcher",
            "--database_path", database_path,
            "--SequentialMatching.overlap", str(props.overlap)
        ]
        self._process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        self.print_logs(self._process)
        if self._process.returncode != 0:
            self.report({'ERROR'}, "Feature matching failed")
            return  # Early exit from the thread function

    
        # Step 4: GLOMAP sparse reconstruction
        self.report({'INFO'}, "Step 4/7: Running sparse reconstruction...")
        self.update_current_step(4)
        print("Step 4/7: Running sparse reconstruction...")
        OPEN_VIDEO_TRACKER_OT_run_pipeline_modal._message = "Step 4/7: Running sparse reconstruction..."
        cmd = [
            prefs.glomap_path,
            "mapper",
            "--database_path", database_path,
            "--image_path", images_dir,
            "--output_path", sparse_dir
        ]
        self._process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        self.print_logs(self._process)
        if self._process.returncode != 0:
            self.report({'ERROR'}, "Sparse reconstruction failed")
            return  # Early exit from the thread function
        

    
        # Step 5: Export TXT inside the model folder
        self.report({'INFO'}, "Step 5/7: Exporting model (internal)...")
        self.update_current_step(5)
        print("Step 5/7: Exporting model (internal)...")
        OPEN_VIDEO_TRACKER_OT_run_pipeline_modal._message = "Step 5/7: Exporting model (internal)..."
        if os.path.exists(model_dir):
            cmd = [
                prefs.colmap_path,
                "model_converter",
                "--input_path", model_dir,
                "--output_path", model_dir,
                "--output_type", "TXT"
            ]
            self._process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            self.print_logs(self._process)
            if self._process.returncode != 0:
                self.report({'ERROR'}, "Internal model export failed")
                return  # Early exit from the thread function

        else:
            # Skip if model doesn't exist
            self.update_current_step(self._current_step + 1)
            self.report({'INFO'}, "Pipeline execution completed successfully")
        
    
        # Step 6: Export TXT to parent sparse directory
        self.report({'INFO'}, "Step 6/7: Exporting model (external)...")
        self.update_current_step(6)
        print("Step 6/7: Exporting model (external)...")
        OPEN_VIDEO_TRACKER_OT_run_pipeline_modal._message = "Step 6/7: Exporting model (external)..."
        if os.path.exists(model_dir):
            cmd = [
                prefs.colmap_path,
                "model_converter",
                "--input_path", model_dir,
                "--output_path", sparse_dir,
                "--output_type", "TXT"
            ]
            self._process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            self.print_logs(self._process)
            if self._process.returncode != 0:
                self.report({'ERROR'}, "External model export failed")
                return  # Early exit from the thread function
        else:
            # Skip if model doesn't exist
            self.update_current_step(self._current_step + 1)
            
    
        # Step 7: Cleanup and finish
        self.report({'INFO'}, "Step 7/7: Finalizing...")
        # This step is just for progress tracking
        self.update_current_step(7)
        print("Step 7/7: Finalizing...")
        OPEN_VIDEO_TRACKER_OT_run_pipeline_modal._message = "Step 7/7: Finalizing..."
        
        # Pipeline completed successfully
        self.report({'INFO'}, "Pipeline execution completed successfully")
                
    def print_logs(self, process):
        # Print output in real-time as it's produced
        for line in iter(process.stdout.readline, ""):
            if line:
                print(f"CMD: {line.rstrip()}")
                # Also report to Blender UI
        process.wait()
        
        # Check if process completed successfully
        if process.returncode != 0:
            self.report({'ERROR'}, f"Command failed with return code {process.returncode}")
            # Note: We can't directly call self.cancel here because we're in a separate thread
            # The calling function should check the return code and handle cancellation
    

    def cancel(self, context):
        # Clean up timer
        OPEN_VIDEO_TRACKER_OT_run_pipeline_modal.is_active = False
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