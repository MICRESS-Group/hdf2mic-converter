hdf2mic
-------

Convert DREAM3D HDF5 synthetic microstructure file
to MICRESS input files TXT and ASCII VTK

The script expects all input arguments for the conversion (conversion parameters)
in form of a standardized JSON file. This file holds all necessary data like input
and output file paths, HDF5 Dataset group paths, and output formatting arguments.
The script is able to generate an empty template JSON file to start from.
See printed help instructions.

The script can either be called directly, or the package can be installed, see setup.py.

Conversion currently supports:
- TXT: phase and euler angles per grain for 2D and 3D structures
- VTK: grainID (kornID) per cell (voxel), optional time

