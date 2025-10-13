import os
import logging

import bpy
from bpy.props import StringProperty , BoolProperty, IntProperty, FloatProperty, EnumProperty, FloatVectorProperty
from bpy.types import Operator
import math

from .camera import Camera
from .camera_utility import add_cameras ,adjust_render_settings_if_possible
from .camera_animation_utility import add_camera_animation
from .object_utility import add_collection

from .point_importer import PointImporter
from .mesh_importer import MeshImporter
from .general_options import GeneralOptions
from .colmap_file_handler import ColmapFileHandler
from .logger import log_info, log_warning, log_error, log_debug, logger

class ImportOperator(bpy.types.Operator):
    """Abstract basic import operator."""

    @staticmethod
    def _is_custom_property(prop):
        custom_property_types = [
            bpy.types.BoolProperty,
            bpy.types.IntProperty,
            bpy.types.FloatProperty,
            bpy.types.StringProperty,
            bpy.types.EnumProperty,
        ]
        return type(prop) in custom_property_types

    def _get_addon_name(self):
        return __name__.split(".")[0]

    def _initialize_options(self, source):
        # Side note:
        #   "vars(my_obj)" does not work in Blender
        #   "dir(my_obj)" shows the attributes, but not the corresponding type
        #   "my_obj.rna_type.properties.items()" lists attribute names with
        #   corresponding types
        for name, prop in source.rna_type.properties.items():
            if name == "bl_idname":
                continue
            if not ImportOperator._is_custom_property(prop):
                continue
            if not hasattr(self, name):
                continue
            setattr(self, name, getattr(source, name))

    def initialize_options_from_addon_preferences(self):
        """Initialize the import options from the current addon preferences."""
        addon_name = self._get_addon_name()
        import_export_prefs = bpy.context.preferences.addons[
            addon_name
        ].preferences
        self._initialize_options(import_export_prefs)

    def get_default_image_path(self, reconstruction_fp, image_dp):
        """Get the (default) path that defines where to look for images."""
        if image_dp is None:
            return None
        elif image_dp == "":
            image_default_same_dp = os.path.dirname(reconstruction_fp)
            image_default_sub_dp = os.path.join(
                image_default_same_dp, "images"
            )
            if os.path.isdir(image_default_sub_dp):
                image_dp = image_default_sub_dp
            else:
                image_dp = image_default_same_dp
        return image_dp

    def execute(self, context):
        """Abstract method that must be overriden by a subclass."""
        # Pythons ABC class and Blender's operators do not work well
        # together in the context of multiple inheritance.
        raise NotImplementedError("Subclasses must override this function!")

class CameraImporter:
    """Importer for cameras and corresponding image information."""

    use_workspace_images: BoolProperty(
        name="Use Workspace Images",
        description="If selected, use the (undistorted) images in the"
        " workspace (if available). Otherwise use the images in the default"
        " image path.",
        default=True,
    )

    image_fp_items = [
        (Camera.IMAGE_FP_TYPE_NAME, "File Name", "", 1),
        (Camera.IMAGE_FP_TYPE_RELATIVE, "Relative Path", "", 2),
        (Camera.IMAGE_FP_TYPE_ABSOLUTE, "Absolute Path", "", 3),
    ]
    image_fp_type: EnumProperty(
        name="Image File Path Type",
        description="Choose how image file paths are treated, "
        "i.e. absolute path, relative path or file name",
        items=image_fp_items,
    )
    image_dp: StringProperty(
        name="Image Directory",
        description="Assuming that the SfM reconstruction result is "
        "located in <some/path/rec.ext> or <some/path/rec_directory>. "
        "The addons uses either <some/path/images> (if available) "
        "or <some/path> as default image path. For MVS reconstruction "
        "results of Colmap, Meshroom or MVE the addon may or may not "
        "search for the images inside the corresponding workspace",
        # Can not use subtype='DIR_PATH' while importing another file
        # (i.e. nvm)
        default="",
    )
    import_cameras: BoolProperty(
        name="Import Cameras", description="Import Cameras", default=True
    )
    default_width: IntProperty(
        name="Default Width",
        description="Width, which will be used used if corresponding "
        "image is not found",
        default=-1,
    )
    default_height: IntProperty(
        name="Default Height",
        description="Height, which will be used used if corresponding "
        "image is not found",
        default=-1,
    )
    default_focal_length: FloatProperty(
        name="Focal length in pixel",
        description="Value for missing focal length in LOG (Open3D) file. ",
        default=float("nan"),
    )
    default_pp_x: FloatProperty(
        name="Principal Point X Component",
        description="Principal Point X Component, which will be used if "
        "not contained in the NVM (VisualSfM) / LOG (Open3D) file. If no "
        "value is provided, the principal point is set to the image "
        "center",
        default=float("nan"),
    )
    default_pp_y: FloatProperty(
        name="Principal Point Y Component",
        description="Principal Point Y Component, which will be used if "
        "not contained in the NVM (VisualSfM) / LOG (Open3D) file. If no "
        "value is provided, the principal point is set to the image "
        "center",
        default=float("nan"),
    )
    add_background_images: BoolProperty(
        name="Add a Background Image for each Camera",
        description="The background image is only visible by viewing the "
        "scene from a specific camera",
        default=True,
    )
    add_image_planes: BoolProperty(
        name="Add an Image Plane for each Camera",
        description="Add an Image Plane for each Camera - only for "
        "non-panoramic cameras",
        default=False,
    )
    add_image_plane_emission: BoolProperty(
        name="Add Image Plane Color Emission",
        description="Add image plane color emission to increase the "
        "visibility of the image planes",
        default=True,
    )
    image_plane_transparency: FloatProperty(
        name="Image Plane Transparency Value",
        description="Transparency value of the image planes: "
        "0 = invisible, 1 = opaque",
        default=0.5,
        min=0,
        max=1,
    )
    add_depth_maps_as_point_cloud: BoolProperty(
        name="Add Depth Maps (EXPERIMENTAL)",
        description="Add the depth map (if available) as point cloud "
        "for each Camera",
        default=False,
    )
    use_default_depth_map_color: BoolProperty(
        name="Use Default Depth Map Color",
        description="If not selected, each depth map is colorized with "
        "a different (random) color",
        default=False,
    )
    depth_map_default_color: FloatVectorProperty(
        name="Depth Map Color",
        description="Depth map color",
        subtype="COLOR",
        size=3,  # RGBA colors are not compatible with the GPU Module
        default=(0.0, 1.0, 0.0),
        min=0.0,
        max=1.0,
    )
    depth_map_display_sparsity: IntProperty(
        name="Depth Map Display Sparsity",
        description="Adjust the sparsity of the depth maps. A value of 10 "
        "means that every 10th depth map value is converted to a 3D point",
        default=10,
        min=1,
    )
    depth_map_id_or_name_str: StringProperty(
        name="Depth Map IDs or Names to Display",
        description="A list of camera indices or names (separated by "
        "whitespaces) used to select the depth maps, which will be "
        "displayed as point clouds. If no indices are provided, all "
        "depth maps are shown. The names must not contain whitespaces",
        default="",
    )
    add_camera_motion_as_animation: BoolProperty(
        name="Add Camera Motion as Animation",
        description="Add an animation reflecting the camera motion. The "
        "order of the cameras is determined by the corresponding file "
        "name",
        default=True,
    )
    animation_frame_source: EnumProperty(
        name="Use original frames",
        items=(
            ("ORIGINAL", "Original Frames", ""),
            ("ADJUSTED", "Adjusted Frames", ""),
        ),
    )
    add_animated_camera_background_images: BoolProperty(
        name="Add Background Images for the Animated Camera",
        description="The background images are only visible by viewing the "
        "scene from the animated camera at the corresponding time step",
        default=True,
    )
    reorganize_undistorted_images: BoolProperty(
        name="Reorganize Undistorted Workspace Images",
        description="Rename the undistorted images according to the original"
        " image names and write them to a single directory. Certain libraries"
        " such as Meshroom or MVE rename or move the undistorted images to"
        " different directories. Thus, the reversal is necessary to use the"
        " images as background sequence for the animated camera."
        " WARNING: This will write a copy of the corresponding images to the"
        " workspace directory",
        default=True,
    )
    number_interpolation_frames: IntProperty(
        name="Number of Frames Between two Reconstructed Cameras",
        description="The poses of the animated camera are interpolated",
        default=0,
        min=0,
    )

    interpolation_items = [
        ("LINEAR", "LINEAR", "", 1),
        ("BEZIER", "BEZIER", "", 2),
        ("SINE", "SINE", "", 3),
        ("QUAD", "QUAD", "", 4),
        ("CUBIC", "CUBIC", "", 5),
        ("QUART", "QUART", "", 6),
        ("QUINT", "QUINT", "", 7),
        ("EXPO", "EXPO", "", 8),
        ("CIRC", "CIRC", "", 9),
        ("BACK", "BACK", "", 10),
        ("BOUNCE", "BOUNCE", "", 11),
        ("ELASTIC", "ELASTIC", "", 12),
        ("CONSTANT", "CONSTANT", "", 13),
    ]
    interpolation_type: EnumProperty(
        name="Interpolation Type",
        description="Blender string that defines the type of the "
        "interpolation",
        items=interpolation_items,
    )

    consider_missing_cameras_during_animation: BoolProperty(
        name="Adjust Frame Numbers of Camera Animation",
        description="Assume there are three consecutive images A,B and "
        "C, but only A and C have been reconstructed. This option "
        "adjusts the frame number of C and the number of interpolation "
        "frames between camera A and C",
        default=True,
    )

    remove_rotation_discontinuities: BoolProperty(
        name="Remove Rotation Discontinuities",
        description="The addon uses quaternions q to represent the "
        "rotation. A quaternion q and its negative -q describe the same "
        "rotation. This option allows to remove different signs",
        default=True,
    )

    suppress_distortion_warnings: BoolProperty(
        name="Suppress Distortion Warnings",
        description="Radial distortion might lead to incorrect alignments "
        "of cameras and points. Enable this option to suppress "
        "corresponding warnings. If possible, consider to re-compute the "
        "reconstruction using a camera model without radial distortion",
        default=True,
    )

    adjust_render_settings: BoolProperty(
        name="Adjust Render Settings",
        description="Adjust the render settings according to the "
        "corresponding images - all images have to be captured with the "
        "same device. If disabled the visualization of the camera cone "
        "in 3D view might be incorrect",
        default=True,
    )

    camera_extent: FloatProperty(
        name="Initial Camera Extent (in Blender Units)",
        description="Initial Camera Extent (Visualization)",
        default=1,
    )

    def draw_camera_options(
        self,
        layout,
        draw_workspace_image_usage=False,
        reorganize_undistorted_images=False,
        draw_image_fp=True,
        draw_depth_map_import=False,
        draw_image_size=False,
        draw_principal_point=False,
        draw_focal_length=False,
        draw_everything=False,
    ):
        """Draw camera import options."""
        camera_box = layout.box()

        if draw_workspace_image_usage or draw_everything:
            camera_box.prop(self, "use_workspace_images")

        if draw_image_fp or draw_everything:
            camera_box.prop(self, "image_fp_type")
            if self.image_fp_type in ["NAME", "RELATIVE"] or draw_everything:
                camera_box.prop(self, "image_dp")

        if (
            draw_focal_length
            or draw_image_size
            or draw_principal_point
            or draw_everything
        ):
            image_box = camera_box.box()
            if draw_focal_length or draw_everything:
                image_box.prop(self, "default_focal_length")
            if draw_image_size or draw_everything:
                image_box.prop(self, "default_width")
                image_box.prop(self, "default_height")
            if draw_principal_point or draw_everything:
                image_box.prop(self, "default_pp_x")
                image_box.prop(self, "default_pp_y")

        import_camera_box = camera_box.box()
        import_camera_box.prop(self, "import_cameras")
        if self.import_cameras or draw_everything:
            import_camera_box.prop(self, "camera_extent")
            import_camera_box.prop(self, "add_background_images")

            image_plane_box = import_camera_box.box()
            image_plane_box.prop(self, "add_image_planes")
            if self.add_image_planes or draw_everything:
                image_plane_box.prop(self, "add_image_plane_emission")
                image_plane_box.prop(self, "image_plane_transparency")

            if draw_depth_map_import or draw_everything:
                depth_map_box = import_camera_box.box()
                depth_map_box.prop(self, "add_depth_maps_as_point_cloud")
                if self.add_depth_maps_as_point_cloud or draw_everything:
                    depth_map_box.prop(self, "use_default_depth_map_color")
                    if self.use_default_depth_map_color or draw_everything:
                        depth_map_box.prop(self, "depth_map_default_color")
                    depth_map_box.prop(self, "depth_map_display_sparsity")
                    depth_map_box.prop(self, "depth_map_id_or_name_str")

        anim_box = camera_box.box()
        anim_box.prop(self, "add_camera_motion_as_animation")

        if self.add_camera_motion_as_animation or draw_everything:
            anim_box.row().prop(self, "animation_frame_source", expand=True)
            if self.animation_frame_source == "ORIGINAL" or draw_everything:
                anim_box.prop(self, "add_animated_camera_background_images")
                if reorganize_undistorted_images or draw_everything:
                    anim_box.prop(self, "reorganize_undistorted_images")
            if self.animation_frame_source == "ADJUSTED" or draw_everything:
                anim_box.prop(self, "number_interpolation_frames")
            anim_box.prop(self, "consider_missing_cameras_during_animation")
            anim_box.prop(self, "interpolation_type")
            anim_box.prop(self, "remove_rotation_discontinuities")

        camera_box.prop(self, "suppress_distortion_warnings")
        camera_box.prop(self, "adjust_render_settings")

    def set_intrinsics_of_cameras(self, cameras):
        """Set intrinsic parameters of cameras.

        This function should be overwritten, if the intrinsic parameters are
        not part of the reconstruction data (e.g. log file).
        """
        success = True
        return cameras, success

    def set_image_size_of_cameras(self, cameras):
        """Set image size of cameras.

        This function should be overwritten, if the image size is not part of
        the reconstruction data (e.g. nvm file).
        """
        success = True
        return cameras, success

    @staticmethod
    def _principal_points_initialized(cameras):
        principal_points_initialized = True
        for camera in cameras:
            if not camera.has_principal_point():
                principal_points_initialized = False
                break
        return principal_points_initialized

    @staticmethod
    def _set_principal_point_for_cameras(
        cameras, default_pp_x, default_pp_y, op=None
    ):
        if not math.isnan(default_pp_x) and not math.isnan(default_pp_y):
            log_warning("Setting principal points to default values!", op)
        else:
            log_warning("Setting principal points to image centers!", op)
            assert (
                cameras[0].width is not None and cameras[0].height is not None
            )
            default_pp_x = cameras[0].width / 2.0
            default_pp_y = cameras[0].height / 2.0

        for camera in cameras:
            if not camera.has_principal_point():
                camera.set_principal_point([default_pp_x, default_pp_y])

    def import_photogrammetry_cameras(self, cameras, parent_collection):
        """Import the cameras using the properties of this class."""
        if not self.import_cameras and not self.add_camera_motion_as_animation:
            return {"FINISHED"}

        cameras, success = self.set_image_size_of_cameras(cameras)
        if not success:
            return {"FINISHED"}

        cameras, success = self.set_intrinsics_of_cameras(cameras)
        if not success:
            return {"FINISHED"}

        # The principal point may be part of the reconstruction data
        if not self.__class__._principal_points_initialized(cameras):
            self.__class__._set_principal_point_for_cameras(
                cameras, self.default_pp_x, self.default_pp_y, self
            )

        if self.adjust_render_settings:
            adjust_render_settings_if_possible(cameras, op=self)

        if self.import_cameras:
            add_cameras(
                cameras,
                parent_collection,
                add_background_images=self.add_background_images,
                add_image_planes=self.add_image_planes,
                add_depth_maps_as_point_cloud=self.add_depth_maps_as_point_cloud,
                camera_scale=self.camera_extent,
                image_plane_transparency=self.image_plane_transparency,
                add_image_plane_emission=self.add_image_plane_emission,
                use_default_depth_map_color=self.use_default_depth_map_color,
                depth_map_default_color=self.depth_map_default_color,
                depth_map_display_sparsity=self.depth_map_display_sparsity,
                depth_map_id_or_name_str=self.depth_map_id_or_name_str,
                op=self,
            )

        if self.add_camera_motion_as_animation:
            add_camera_animation(
                cameras=cameras,
                parent_collection=parent_collection,
                animation_frame_source=self.animation_frame_source,
                add_background_images=self.add_animated_camera_background_images,
                reorganize_undistorted_images=self.reorganize_undistorted_images,
                number_interpolation_frames=self.number_interpolation_frames,
                interpolation_type=self.interpolation_type,
                remove_rotation_discontinuities=self.remove_rotation_discontinuities,
                consider_missing_cameras_during_animation=self.consider_missing_cameras_during_animation,
                image_dp=self.image_dp,
                image_fp_type=self.image_fp_type,
                op=self,
            )
        return {"FINISHED"}


class ImportColmapOperator(
    ImportOperator,
    CameraImporter,
    PointImporter,
    MeshImporter,
    GeneralOptions,
):
    """:code:`Blender` operator to import a :code:`Colmap` model/workspace."""

    bl_idname = "import_scene.open_video_tracker_colmap"
    bl_label = "Import Colmap Model Folder"
    bl_options = {"PRESET"}

    directory: StringProperty()
    # filter_folder : BoolProperty(default=True, options={'HIDDEN'})

    def execute(self, context):
        """Import a :code:`Colmap` model/workspace."""
        # Get the suppress_distortion_warnings value from scene properties
        suppress_warnings = context.scene.open_video_tracker.camera_importer.suppress_distortion_warnings

        # Set console handler level based on suppress_distortion_warnings
        # When True, only show warnings and errors; when False, show info and above
        console_handler = None
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                console_handler = handler
                break
        if console_handler:
            if suppress_warnings:
                console_handler.setLevel(logging.WARNING)
            else:
                console_handler.setLevel(logging.INFO)

        path = self.directory
        # Remove trailing slash
        path = os.path.dirname(path)
        log_info("path: " + str(path), self)

        self.image_dp = self.get_default_image_path(path, self.image_dp)
        cameras, points, mesh_ifp = ColmapFileHandler.parse_colmap_folder(
            path,
            self.use_workspace_images,
            self.image_dp,
            self.image_fp_type,
            self.suppress_distortion_warnings,
            self,
        )

        log_info("Number cameras: " + str(len(cameras)), self)
        log_info("Number points: " + str(len(points)), self)
        log_info("Mesh file path: " + str(mesh_ifp), self)

        reconstruction_collection = add_collection("Reconstruction Collection")
        self.import_photogrammetry_cameras(cameras, reconstruction_collection)
        self.import_photogrammetry_points(points, reconstruction_collection)
        self.import_photogrammetry_mesh(mesh_ifp, reconstruction_collection)
        self.apply_general_options()

        return {"FINISHED"}

    def invoke(self, context, event):
        """Set the default import options before running the operator."""
        self.initialize_options_from_addon_preferences()
        # See:
        # https://blender.stackexchange.com/questions/14738/use-filemanager-to-select-directory-instead-of-file/14778
        # https://docs.blender.org/api/current/bpy.types.WindowManager.html#bpy.types.WindowManager.fileselect_add
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        """Draw the import options corresponding to this operator."""
        layout = self.layout
        self.draw_camera_options(
            layout, draw_workspace_image_usage=True, draw_depth_map_import=True
        )
        self.draw_point_options(layout)
        self.draw_mesh_options(layout)
        self.draw_general_options(layout)
