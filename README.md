# Open Video Tracker

A Blender addon for automated video tracking using COLMAP and GLOMAP photogrammetry tools.

## Overview

Open Video Tracker is a Blender addon that automates the process of converting video footage into 3D point clouds and camera tracks. It integrates industry-standard photogrammetry tools (FFmpeg, COLMAP, and GLOMAP) into Blender's interface, allowing users to easily process videos for visual effects, motion tracking, and 3D reconstruction workflows.

## Features

- **Integrated UI**: Access all functionality directly within Blender's 3D Viewport
- **Configurable Parameters**: Adjust frame extraction quality, feature detection settings, and matching parameters
- **Automated Pipeline**: One-click execution of the complete photogrammetry workflow
- **Progress Tracking**: Real-time progress updates during processing
- **Error Handling**: Comprehensive error reporting and graceful failure handling
- **Blender-Compatible Output**: Generates TXT files that can be directly imported into Blender

## Documentation

For detailed information on using and troubleshooting the addon, please refer to the following documentation:

- [User Guide](USER_GUIDE.md) - Complete instructions for installation, configuration, and usage
- [Testing Procedure](TESTING_PROCEDURE.md) - Guidelines for testing the addon functionality
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Solutions for common issues and problems

## Quick Start

### Requirements

- Blender 2.93 or later
- FFmpeg executable
- COLMAP executable
- GLOMAP executable

### Installation

1. Download or clone this repository
2. In Blender, go to Edit → Preferences → Add-ons
3. Click "Install..." and select the `open_video_tracker` folder
4. Enable the addon by checking the checkbox

### Setup

Before using the addon, you need to configure the paths to the required executables:

1. Go to Edit → Preferences → Add-ons
2. Find "Open Video Tracker" in the list
3. Click the arrow to expand the preferences
4. Set the paths to your FFmpeg, COLMAP, and GLOMAP executables

### Usage

1. Open the 3D Viewport and switch to the "Open Video Tracker" tab
2. Click the folder icon to select a video file
3. Adjust the processing parameters as needed:
   - **Frame Rate**: Frames per second to extract from the video
   - **Quality**: Quality factor for frame extraction (1=highest, 31=lowest)
   - **Max Image Size**: Maximum dimension for feature extraction
   - **Use GPU**: Enable GPU acceleration for feature extraction
   - **Overlap**: Number of overlapping frames for sequential matching
4. Click "Run Pipeline" to start processing
5. Monitor progress in the progress bar
6. Once complete, the results will be saved in a structured directory relative to your .blend file

## Output Structure

The addon creates the following directory structure relative to your .blend file:

```
{blend_file_directory}/video_tracking/{video_name}/
├── images/
│   ├── frame_000001.jpg
│   ├── frame_000002.jpg
│   └── ...
├── sparse/
│   ├── cameras.txt
│   ├── images.txt
│   ├── points3D.txt
│   └── 0/
│       ├── cameras.txt
│       ├── images.txt
│       └── points3D.txt
└── database.db
```

## Importing Results into Blender

After processing is complete, you can import the results into Blender:

1. Go to File → Import → COLMAP Model
2. Navigate to the `sparse/0/` directory
3. Select the `cameras.txt`, `images.txt`, and `points3D.txt` files
4. Adjust import settings as needed
5. Click "Import COLMAP Model"

## Troubleshooting

### Common Issues

1. **"Process failed" errors**: Check that all executable paths are correctly configured in the addon preferences
2. **Missing DLL errors**: Ensure all required dependencies for COLMAP and GLOMAP are installed
3. **Permission errors**: Make sure Blender has permission to write to the output directory
4. **Out of memory errors**: Reduce the "Max Image Size" parameter or process shorter videos

### Getting Help

If you encounter issues not covered here, please check the Blender console for detailed error messages. You can access the console through Window → Toggle System Console.

For more detailed troubleshooting, refer to our [Troubleshooting Guide](TROUBLESHOOTING.md).

## License

This addon is released under the MIT License. See the LICENSE file for details.

## Credits

Developed by the Open Video Tracker Team.
Inspired by the workflow_glopmap.bat script by polyfjord.