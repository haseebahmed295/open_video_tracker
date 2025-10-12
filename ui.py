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
        row.prop(open_video_tracker, "quality")
        box = layout.box()

        # COLMAP Feature Extraction Settings
        box.label(text="Feature Extraction", icon='POINTCLOUD_DATA')
        row = box.row(align=True)
        col1 = row.column(align=True)
        col2 = row.column(align=True)
        col1.label(text="Max Image Size")
        col1.label(text="Use GPU")
        col1.label(text="Camera Model")
        col1.label(text="Max Num Features")    
        col2.prop(open_video_tracker, "max_image_size" , text="")
        col2.prop(open_video_tracker, "use_gpu", text="")
        col2.prop(open_video_tracker, "camera_model", text="")
        col2.prop(open_video_tracker, "max_num_features", text="")
        
        # COLMAP Sequential Matching Settings
        box = layout.box()
        box.label(text="Sequential Matching", icon='CON_FOLLOWPATH')
        row = box.row()
        row.prop(open_video_tracker, "overlap")

        # GLOMAP Reconstruction Settings
        box = layout.box()
        box.label(text="Reconstruction", icon='MESH_CUBE')
        row = box.row(align=True)
        col1 = row.column(align=True)
        col2 = row.column(align=True)
        col1.label(text="Max Tracks")
        col2.prop(open_video_tracker, "max_num_tracks" , text="")
        col1.label(text="Constraint Type")
        col2.prop(open_video_tracker, "constraint_type" , text="")
        # Advanced GLOMAP Options
        header,panel = box.panel("A" , default_closed =True)
        header.label(text="Advanced Options", icon='PREFERENCES')
        if panel:
            row = panel.row(align=True)
            col1 = row.column(align=True)
            col2 = row.column(align=True)
            col2.scale_x = 0.6

            col1.label(text="Max Epipolar Error")
            col2.prop(open_video_tracker, "max_epipolar_error" , text="")
            col1.label(text="Max Global Positioning Iterations")
            col2.prop(open_video_tracker, "max_global_positioning_iterations" , text="")
            col1.label(text="Max Bundle Adjustment Iterations")
            col2.prop(open_video_tracker, "max_bundle_adjustment_iterations" , text="")

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