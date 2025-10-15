# Open Video Tracker User Guide

## Introduction

Open Video Tracker is a Blender addon that automates the process of converting video footage into 3D point clouds and camera tracks using photogrammetry techniques. The addon integrates FFmpeg, COLMAP, and GLOMAP to provide a streamlined workflow for video tracking and 3D reconstruction.

## Installation

### Step 1: Download the Addon

1. Download Open Video Tracker addon file (only avalible on windows for now!)
      - Download cuda version if you have a Rtx Nvidia GPU
      - Else download normal version
3. Locate the `open_video_tracker` folder containing the addon files

### Step 2: Install in Blender

1. Open Blender
2. Go to **Edit → Preferences**
3. Select the **Add-ons** tab
4. Click **Addon Settings [^]**
5. Install from disk
6. Navigate to and select the `open_video_tracker` folder
7. Click **Install From Disk**

### Step 4: Verify Installation

1. Switch to the 3D Viewport
2. Look for the "Open Video Tracker" tab in the right sidebar
3. If visible, the installation was successful

## User Interface Pverview
<img width="347" height=full alt="image" src="https://github.com/user-attachments/assets/a7db1b90-81ba-40e9-8587-4d5447118430" />
<img width="350" height=full alt="image" src="https://github.com/user-attachments/assets/4728c200-9fb3-4f4e-a07a-f0dc420cbd2d" />



### Main Panel

The main interface is located in the 3D Viewport sidebar under the "Open Video Tracker" tab.

#### Video Selection Section
- **Video Path**: File browser to select input video file
- **Video Information**: Displays frame rate, resolution, and bitrate (populated automatically)

#### Frame Extraction Settings
- **Quality**: Preset quality levels for frame extraction (Native, High, Balanced, Low, Lowest)

#### Feature Extraction Settings
- **Max Image Size**: Maximum dimension for feature extraction (default: 2000px)
- **Use GPU**: Enable GPU acceleration for feature extraction (if you have cuda version)  
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

### Progress
- Each step is logged to the Blender console
- Processing can be monitored via **Window → Toggle System Console**

### Expected Output

The addon uses same dir as th blend file and creates following directory structure:

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

### Point Cloud Processing
- Comming soon

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

