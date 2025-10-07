import bpy

from .operators import OPEN_VIDEO_TRACKER_OT_run_pipeline_modal

class OPEN_VIDEO_TRACKER_PT_panel(bpy.types.Panel):
    """Creates a Panel in the 3D Viewport"""
    bl_label = "Open Video Tracker"
    bl_idname = "OPEN_VIDEO_TRACKER_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Open Video Tracker"

    def draw(self, context):
        layout = self.layout
    
        scene = context.scene
        open_video_tracker = scene.open_video_tracker
        
        # Video Selection Section
        layout.label(text="Video Selection", icon='FILE_MOVIE')
        row = layout.row()
        row.scale_y = 1.5
        row.scale_x = 1.5
        row.prop(open_video_tracker, "video_path" , text="")
        
        layout = self.layout.column(align=True)
        # Video Information Section
        if open_video_tracker.video_path and open_video_tracker.video_frame_rate:
            box = layout.box()
            box.scale_y = 0.7
            box.label(text="Video Information", icon='INFO')
            
            # Frame Rate
            if open_video_tracker.video_frame_rate:
                row = box.row()
                row.label(text="Frame Rate:")
                row.label(text=open_video_tracker.video_frame_rate)
            
            # Resolution
            if open_video_tracker.video_resolution:
                row = box.row()
                row.label(text="Resolution:")
                row.label(text=open_video_tracker.video_resolution)
            
            # Bitrate
            if open_video_tracker.video_bitrate:
                row = box.row()
                row.label(text="Bitrate:")
                row.label(text=open_video_tracker.video_bitrate)


        box = layout.box()
        # Frame Extraction Settings
        box.label(text="Frame Extraction", icon='IMAGE_DATA')
        row = box.row()
        row.prop(open_video_tracker, "frame_rate")
        row = box.row()
        row.prop(open_video_tracker, "quality")
        
        # COLMAP Feature Extraction Settings
        box.label(text="COLMAP Feature Extraction", icon='POINTCLOUD_DATA')
        row = box.row()
        row.prop(open_video_tracker, "max_image_size")
        row = box.row()
        row.prop(open_video_tracker, "use_gpu")
        
        # COLMAP Sequential Matching Settings
        box.label(text="COLMAP Sequential Matching", icon='CON_FOLLOWPATH')
        row = box.row()
        row.prop(open_video_tracker, "overlap")
        
        # Execution Controls
        box = layout.box()
        box.label(text="Execution", icon='PLAY')
        row = box.row()
        if not OPEN_VIDEO_TRACKER_OT_run_pipeline_modal.is_active:
            row.operator(OPEN_VIDEO_TRACKER_OT_run_pipeline_modal.bl_idname, text="Track Video")
        else:
            row.label(text="Progesss")
            row = box.row()
            row.progress(text=OPEN_VIDEO_TRACKER_OT_run_pipeline_modal._message, factor=open_video_tracker.progress/7)