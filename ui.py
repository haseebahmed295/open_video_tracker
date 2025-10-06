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
        box = layout.box()
        box.label(text="Video Selection", icon='FILE_MOVIE')
        row = box.row()
        row.prop(open_video_tracker, "video_path")
        row.operator("open_video_tracker.select_video", text="", icon='FILEBROWSER')
        
        # Frame Extraction Settings
        box = layout.box()
        box.label(text="Frame Extraction", icon='IMAGE_DATA')
        row = box.row()
        row.prop(open_video_tracker, "frame_rate")
        row = box.row()
        row.prop(open_video_tracker, "quality")
        
        # COLMAP Feature Extraction Settings
        box = layout.box()
        box.label(text="COLMAP Feature Extraction", icon='POINTCLOUD_DATA')
        row = box.row()
        row.prop(open_video_tracker, "max_image_size")
        row = box.row()
        row.prop(open_video_tracker, "use_gpu")
        
        # COLMAP Sequential Matching Settings
        box = layout.box()
        box.label(text="COLMAP Sequential Matching", icon='CON_FOLLOWPATH')
        row = box.row()
        row.prop(open_video_tracker, "overlap")
        
        # GLOMAP Mapper Settings
        box = layout.box()
        box.label(text="GLOMAP Mapper", icon='MOD_MESHDEFORM')
        # Placeholder for GLOMAP options
        
        # Execution Controls
        box = layout.box()
        box.label(text="Execution", icon='PLAY')
        row = box.row()
        row.operator(OPEN_VIDEO_TRACKER_OT_run_pipeline_modal.bl_idname, text="Run Pipeline")
        