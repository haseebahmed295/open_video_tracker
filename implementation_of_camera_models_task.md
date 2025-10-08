# Advanced Feature Extraction and Reconstruction Implementation

## Overview
Added comprehensive camera model support and advanced feature extraction/reconstruction options for improved 3D reconstruction quality and control.

## Changes Made

### 1. Properties (`properties.py`)

#### Camera Models
- Added `camera_model` EnumProperty with all 12 camera models with descriptions and examples:
  - SIMPLE_PINHOLE: High-quality DSLR cameras with prime lenses
  - PINHOLE: Professional cinema cameras
  - SIMPLE_RADIAL: iPhone/Samsung smartphone cameras
  - SIMPLE_RADIAL_FISHEYE: GoPro Hero action cameras
  - RADIAL: Mirrorless cameras with zoom lenses
  - RADIAL_FISHEYE: Insta360 or Ricoh Theta 360° cameras
  - OPENCV: Webcam, security cameras
  - OPENCV_FISHEYE: Wide-angle security cameras
  - FULL_OPENCV: Machine vision, robotics applications
  - FOV: DJI drone cameras, wide-angle photography
  - THIN_PRISM_FISHEYE: Specialized scientific cameras
  - RAD_TAN_THIN_PRISM_FISHEYE: Advanced robotics, VR camera systems

#### Feature Extraction Settings
- Added `max_num_features`: Maximum number of features to extract per image (100-50,000, default: 8,192)

#### GLOMAP Reconstruction Settings
- Added `max_num_tracks`: Maximum number of tracks for reconstruction (1,000-100,000, default: 10,000)
- Added `constraint_type`: Type of constraints for reconstruction:
  - ONLY_POINTS: Use only point constraints
  - ONLY_CAMERAS: Use only camera constraints
  - POINTS_AND_CAMERAS_BALANCED: Balanced point and camera constraints (default)
  - POINTS_AND_CAMERAS: Use both point and camera constraints

### 2. Operators (`operators.py`)

#### COLMAP Feature Extraction
- Updated feature_extractor command to include:
  - `--ImageReader.camera_model` for camera-specific distortion handling
  - `--SiftExtraction.max_num_features` for controlling feature density

#### GLOMAP Reconstruction
- Updated mapper command to include:
  - `--TrackEstablishment.max_num_tracks` for track management
  - `--constraint_type` for reconstruction constraint strategy

### 3. UI (`ui.py`)
- **Feature Extraction section**: Added max features control and camera model selection
- **Reconstruction section**: Added max tracks and constraint type controls
- Organized settings into logical groups for better user experience

## Technical Details

### Camera Model Integration
The feature extraction command now includes:
```bash
--ImageReader.camera_model [selected_model]
```

This allows COLMAP to use the appropriate camera model for feature extraction, which affects:
- Distortion correction
- Feature matching accuracy
- 3D reconstruction quality

### Default Setting
- Default camera model is set to `SIMPLE_PINHOLE` for basic compatibility
- Users can change this based on their camera type and use case

## Usage

### Camera Model Selection
1. In the Open Video Tracker panel, navigate to "Feature Extraction" settings
2. Select the appropriate camera model from the dropdown based on your camera type:
   - **SIMPLE_PINHOLE**: High-quality DSLR with prime lenses
   - **PINHOLE**: Professional cinema cameras
   - **SIMPLE_RADIAL**: Smartphone cameras (iPhone/Samsung)
   - **SIMPLE_RADIAL_FISHEYE**: GoPro action cameras
   - **OPENCV**: Webcams, security cameras
   - **FISHEYE models**: 360° cameras, wide-angle lenses
   - **Specialized models**: Machine vision, robotics, VR systems

### Advanced Feature Settings
1. **Max Features**: Control feature density (100-50,000 features per image)
   - Lower values (1,000-4,000): Faster processing, less memory usage
   - Higher values (8,000-20,000): Better accuracy, more processing time
   - Default: 8,192 (balanced performance)

### Reconstruction Settings
1. **Max Tracks**: Set maximum tracks for GLOMAP reconstruction (1,000-100,000)
   - Lower values: Faster reconstruction, may miss some features
   - Higher values: More accurate but slower processing
   - Default: 10,000

2. **Constraint Type**: Choose reconstruction strategy:
   - **POINTS_ONLY**: Focus on point constraints only
   - **CAMERAS_ONLY**: Focus on camera constraints only
   - **POINTS_AND_CAMERAS_BALANCED**: Balanced approach (recommended)
   - **POINTS_AND_CAMERAS**: Use all available constraints

## Benefits
- **Camera-specific optimization**: Improved feature extraction accuracy for different camera types
- **Better distortion handling**: Proper lens distortion correction based on camera model
- **Enhanced 3D reconstruction quality**: More accurate and robust reconstruction
- **Flexible feature control**: Adjust feature density based on processing requirements
- **Advanced reconstruction options**: Fine-tune reconstruction strategy for different scenarios
- **Support for specialized equipment**: Drones, action cameras, professional cinema cameras, robotics