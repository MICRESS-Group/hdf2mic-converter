# hdf2mic

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


## Installation

hdf2mic requires Python 2.7

Additional packages:

* numpy
* h5py

## Execution

Generate a configuration template file 'myConfiguration.json':  

python hdf2mic.py template ./myConfiguration.json

Convert with:

python hdf2mic.py convert ./myConfiguration.json

## Acknowledgements

Thanks to [Johannes Wasmer](https://github.com/Irratzo), the original author of this code.

The authors acknowledge funding of the present work by the European Commission within the 
MarketPlace project (Grant ID H2020-NMBP-25-2017 760173).
