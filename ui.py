import bpy

from .properties import OpenVideoTrackerCameraProperties , OpenVideoTrackerPointsProperties

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


class OPEN_VIDEO_TRACKER_PT_camera_panel(bpy.types.Panel):
    """Creates a Panel in the 3D Viewport"""
    bl_label = "Import Options"
    bl_idname = "OPEN_VIDEO_TRACKER_PT_camera_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = "Open Video Tracker"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        # row.scale_y = 1.5
        self.draw_camera_options(row , scene.open_video_tracker.camera_importer)
        self.draw_point_options(layout , scene.open_video_tracker.point_importer)
    def draw_camera_options(
        self,
        layout,
        prop:OpenVideoTrackerCameraProperties,
    ):
        """Draw camera import options."""
        camera_box = layout.box()
        prop = prop

        import_camera_box = camera_box.box()
        import_camera_box.prop(prop, "import_cameras")
        if prop.import_cameras:
            import_camera_box.prop(prop, "camera_extent")
            import_camera_box.prop(prop, "add_background_images")

            image_plane_box = import_camera_box.box()
            image_plane_box.prop(prop, "add_image_planes")
            if prop.add_image_planes:
                image_plane_box.prop(prop, "add_image_plane_emission")
                image_plane_box.prop(prop, "image_plane_transparency")

        anim_box = camera_box.box()
        anim_box.prop(prop, "add_camera_motion_as_animation")

        if prop.add_camera_motion_as_animation:
            anim_box.row().prop(prop, "animation_frame_source", expand=True)
            if prop.animation_frame_source == "ORIGINAL":
                anim_box.prop(prop, "add_animated_camera_background_images")
            if prop.animation_frame_source == "ADJUSTED":
                anim_box.prop(prop, "number_interpolation_frames")
            anim_box.prop(prop, "consider_missing_cameras_during_animation")
            anim_box.prop(prop, "interpolation_type")
            anim_box.prop(prop, "remove_rotation_discontinuities")

        camera_box.prop(prop, "suppress_distortion_warnings")
        camera_box.prop(prop, "adjust_render_settings")

    def draw_point_options(self, layout, prop:OpenVideoTrackerPointsProperties):
        """Draw point import options."""
        point_box = layout.box()
        point_box.prop(prop, "import_points")
        point_box.prop(prop, "point_cloud_display_sparsity")
        point_box.prop(prop, "center_points")
        if prop.import_points:
            opengl_box = point_box.box()
            opengl_box.prop(prop, "draw_points_with_gpu")
            if prop.draw_points_with_gpu:
                opengl_box.prop(prop, "add_points_to_point_cloud_handle")
                opengl_box.prop(prop, "point_size")
            mesh_box = point_box.box()
            mesh_box.prop(prop, "add_points_as_mesh_oject")
            if prop.add_points_as_mesh_oject:
                mesh_box.prop(prop, "add_mesh_to_point_geometry_nodes")
                mesh_box.prop(prop, "point_radius")
                mesh_box.prop(prop, "point_subdivisions")
                mesh_box.prop(prop, "add_color_as_custom_property")
