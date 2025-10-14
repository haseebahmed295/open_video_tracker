# Open Video Tracker User Guide

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [User Interface Overview](#user-interface-overview)
- [Workflow](#workflow)
- [Configuration Options](#configuration-options)
- [Running the Pipeline](#running-the-pipeline)
- [Importing Results](#importing-results)
- [Post-Processing](#post-processing)
- [Best Practices](#best-practices)

## Introduction

Open Video Tracker is a Blender addon that automates the process of converting video footage into 3D point clouds and camera tracks using photogrammetry techniques. The addon integrates FFmpeg, COLMAP, and GLOMAP to provide a streamlined workflow for video tracking and 3D reconstruction.

## Installation

### Step 1: Download the Addon

1. Download or clone the Open Video Tracker repository
2. Locate the `open_video_tracker` folder containing the addon files

### Step 2: Install in Blender

1. Open Blender
2. Go to **Edit → Preferences**
3. Select the **Add-ons** tab
4. Click **Install...**
5. Navigate to and select the `open_video_tracker` folder
6. Click **Install Add-on**

### Step 3: Enable the Addon

1. In the Add-ons list, find **"Open Video Tracker"**
2. Check the checkbox to enable the addon
3. The addon should now appear in the 3D Viewport sidebar under "Open Video Tracker"

### Step 4: Verify Installation

1. Switch to the 3D Viewport
2. Look for the "Open Video Tracker" tab in the right sidebar
3. If visible, the installation was successful


## User Interface Overview

### Main Panel

The main interface is located in the 3D Viewport sidebar under the "Open Video Tracker" tab.

#### Video Selection Section
- **Video Path**: File browser to select input video file
- **Video Information**: Displays frame rate, resolution, and bitrate (populated automatically)

#### Frame Extraction Settings
- **Quality**: Preset quality levels for frame extraction (Native, High, Balanced, Low, Lowest)

#### Feature Extraction Settings
- **Max Image Size**: Maximum dimension for feature extraction (default: 2000px)
- **Use GPU**: Enable GPU acceleration for feature extraction
- **Camera Model**: Camera distortion model (Simple Radial recommended for most cases)
- **Max Num Features**: Maximum features to extract per image (default: 8192)

#### Sequential Matching Settings
- **Overlap**: Number of overlapping frames for sequential matching (default: 10)

#### Reconstruction Settings
- **Max Tracks**: Maximum tracks per image (default: 1000)
- **Constraint Type**: Balance between point and camera constraints
- **Advanced Options**: Additional GLOMAP parameters (epipolar error, iterations)

#### Execution Controls
- **Track Video**: Button to start the processing pipeline
- **Progress**: Real-time progress indicator during processing

### Import Options Panel

Located in the collapsible "Import Options" panel:

#### Camera Import Settings
- **Import Cameras**: Enable camera track import
- **Camera Extent**: Size of camera visualization
- **Add Background Images**: Include original frames as background
- **Add Image Planes**: Create image plane objects
- **Animation Options**: Camera motion animation settings

#### Point Import Settings
- **Import Points**: Enable point cloud import
- **Point Cloud Display**: Sparsity and rendering options
- **GPU Rendering**: Hardware-accelerated point display
- **Mesh Options**: Convert points to mesh objects

## Workflow

### Step 1: Prepare Your Video

1. Ensure your video file is in a supported format (MP4, AVI, MOV, MKV, WMV, FLV, WebM)
2. For best results:
   - Use high-quality, stable footage
   - Avoid excessive camera movement or shaky footage
   - Ensure good lighting and contrast
   - Keep video length reasonable (start with short clips for testing)

### Step 2: Configure Processing Settings

1. **Video Quality**: Choose based on your needs and hardware
   - Native/High: Best quality, largest files, slowest processing
   - Balanced: Good quality/performance balance
   - Low/Lowest: Fast processing, smaller files

2. **Feature Extraction**:
   - Increase Max Image Size for high-resolution videos
   - Enable GPU if available for faster processing
   - Choose appropriate camera model based on your camera type

3. **Reconstruction**:
   - Adjust Max Tracks based on scene complexity
   - Use Balanced constraint type for most scenarios

### Step 3: Run the Pipeline

1. Click **"Track Video"** to start processing
2. Monitor progress in the progress bar
3. Processing time varies based on video length and settings
4. Do not close Blender during processing

### Step 4: Import Results

After processing completes, the results are automatically imported. The addon creates:

- Camera objects with animation data
- Point cloud data
- Background images (if enabled)

## Configuration Options

### Frame Extraction Quality

| Quality | QScale | Use Case |
|---------|--------|----------|
| Native | 1 | Highest quality, archival |
| High | 2 | High quality production |
| Balanced | 4 | General purpose |
| Low | 8 | Fast preview, testing |
| Lowest | 16 | Very fast, low quality |

### Camera Models

Choose the appropriate camera model based on your camera type:

- **Simple Radial**: Most consumer cameras (smartphones, DSLRs)
- **Simple Radial Fisheye**: Action cameras (GoPro)
- **OpenCV**: Computer vision cameras
- **Full OpenCV**: Complex distortion scenarios

### Constraint Types

- **Points Only**: Use when camera positions are unreliable
- **Cameras Only**: Use when point features are sparse
- **Balanced**: Recommended for most scenarios
- **Points and Cameras**: Maximum constraints, slower processing

## Running the Pipeline

### Processing Steps

The pipeline consists of 7 main steps:

1. **Frame Extraction**: FFmpeg extracts frames from video
2. **Feature Extraction**: COLMAP detects feature points
3. **Feature Matching**: COLMAP matches features across frames
4. **Sparse Reconstruction**: GLOMAP creates 3D point cloud
5. **Model Export**: Export camera and point data
6. **Finalization**: Cleanup and preparation for import

### Monitoring Progress

- Progress is shown as a percentage (0-100%)
- Each step is logged to the Blender console
- Processing can be monitored via **Window → Toggle System Console**

### Expected Output

The addon creates a directory structure:

```
{your_blend_file_directory}/
└── video_tracking/
    └── {video_name}/
        ├── images/          # Extracted frames
        ├── sparse/          # Reconstruction data
        │   ├── 0/          # Model files
        │   └── cameras.txt # Camera data
        │   └── images.txt  # Image data
        │   └── points3D.txt # Point cloud data
        └── database.db     # COLMAP database
```

## Importing Results

### Automatic Import

The addon automatically imports results when processing completes. However, you can also manually import using Blender's built-in COLMAP importer:

1. Go to **File → Import → COLMAP Model**
2. Navigate to the `sparse/0/` directory
3. Select the TXT files
4. Configure import options
5. Click **Import COLMAP Model**

### Import Options

#### Camera Import
- **Camera Extent**: Visual size of camera objects
- **Background Images**: Show original frames
- **Image Planes**: Create textured planes
- **Animation**: Convert camera motion to keyframes

#### Point Cloud Import
- **Display Sparsity**: Reduce point density for performance
- **GPU Rendering**: Hardware-accelerated display
- **Mesh Conversion**: Convert points to mesh objects

## Post-Processing

### Camera Track Refinement

1. Select camera objects in the scene
2. Use Blender's animation tools to adjust camera motion
3. Apply smoothing or stabilization if needed
4. Fine-tune camera positions for specific shots

### Point Cloud Processing

1. Use Blender's mesh editing tools on point cloud data
2. Apply decimation to reduce point count
3. Clean up noise or outliers
4. Convert to mesh for further modeling

### Integration with VFX Pipeline

1. Export camera data for use in other software
2. Use point cloud as reference for modeling
3. Create motion paths for character animation
4. Generate depth maps from point cloud data

## Best Practices

### Video Preparation

- **Resolution**: Higher resolution provides better tracking but increases processing time
- **Frame Rate**: 24-30 fps is optimal; higher rates may not improve tracking significantly
- **Stabilization**: Use stabilized footage when possible
- **Lighting**: Ensure consistent, even lighting
- **Motion**: Smooth camera movement works better than jerky motion

### Processing Optimization

- **Start Small**: Test with short video clips first
- **GPU Usage**: Enable GPU acceleration when available
- **Quality Settings**: Use Balanced quality for initial tests
- **Memory Management**: Monitor RAM usage with large videos

### Scene Considerations

- **Feature-Rich**: Scenes with lots of texture and detail track better
- **Motion Blur**: Minimize motion blur for better feature detection
- **Scale**: Include objects of known size for scale reference
- **Overlap**: Ensure sufficient scene overlap between frames


### Quick Fixes

- **Processing Fails**: Check executable paths in preferences
- **Out of Memory**: Reduce Max Image Size or use lower quality
- **Poor Tracking**: Adjust camera model or increase Max Features
- **Slow Processing**: Enable GPU or reduce video resolution

