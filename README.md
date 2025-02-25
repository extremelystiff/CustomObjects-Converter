# CustomObjects Converter

A GUI application for converting CSV files of static mesh actors to CustomObjects mod configuration format for Insurgency: Sandstorm.

## Overview

This tool helps you convert exported CSV files containing static mesh actor data into the proper format for the CustomObjects mutator. It handles multiple maps/scenarios and automatically filters out problematic assets that could cause the game to crash.

## Features

- User-friendly graphical interface
- Support for multiple CSV files with different scenario names
- Automatic filtering of problematic assets (doors, windows, merged meshes, signs, and more)
- Proper rotation handling (Roll-Pitch-Yaw format)
- Consolidated output with unique asset indexing
- Option to add "Once" parameter to all Blueprint assets (prevents respawning)
- Option to filter out ALL Blueprint assets (StaticMesh only mode)
- Detailed conversion log

## Installation

### Requirements
- Python 3.6 or higher
- Tkinter (usually included with Python)

### Running the Program

1. Save the script to a file named `convert_gui.py`
2. Run it with Python:
   ```
   python convert_gui.py
   ```

## Usage Instructions

1. **Add CSV Files**: Click "Add CSV" to select one or more CSV files containing exported static mesh data
2. **Set Scenario Names**: Select each CSV file in the list and set its corresponding scenario name
   - Example scenario name: `Scenario_Precinct_Push_Security`
3. **Configure Options**:
   - Check "Add 'Once' parameter to all Blueprint assets" to prevent Blueprint objects from respawning
   - Check "Filter out ALL Blueprint assets" to only use static meshes (more stable)
4. **Select Output File**: Click "Browse..." to choose where to save the INI file
5. **Start Conversion**: Click the "CONVERT" button
6. **Monitor Progress**: The log on the right will show progress and any issues encountered

### CSV Format

The tool expects CSV files in the format exported by the Unreal Engine actor dump:

```
---,Actor,Location,Rotation,Scale,Meshes
Row_0,Class'/Script/Engine.StaticMeshActor',"(X=2342.699463,Y=23046.531250,Z=-345.043182)","(Pitch=0.000007,Yaw=-180.000168,Roll=90.000031)","(X=1.000000,Y=1.000000,Z=1.000000)","((StaticMesh=StaticMesh'/Game/Environment/Props/Exterior/Generic/SM_WoodPanel_01a.SM_WoodPanel_01a'',Materials=(MaterialInstanceConstant'""/Game/Environment/Props/Exterior/Generic/Materials/MI_RebarsWood_01""')))"
```

## Filtered Assets

The converter automatically skips these types of assets to prevent crashes:
- Doors and windows
- Merged static meshes
- Traffic signs and other signs
- Light-related blueprints (lanterns, bulbs, etc.)
- Breakable objects
- ShockwaveReactions objects
- Weapons, vehicles, and characters
- Many other problematic blueprint types

## Stability Notes

If you're experiencing crashes:
1. Try using the "Add 'Once' parameter" option first, which can help with blueprint stability
2. If crashes persist, enable the "Filter out ALL Blueprint assets" option for maximum stability
3. Some static mesh assets might still cause issues - check the logs for any patterns in crashes

## Notes

- Objects at location (0,0,0) are automatically skipped
- Duplicate assets across different maps will be included only once in the output
- Each asset type (Blueprint/StaticMesh) has its own index starting from 0
