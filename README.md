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

python template ./myConfiguration.json

Convert with:

python convert ./myConfiguration.json

## Acknowledgements

Thanks to [Johannes Wasmer](https://github.com/Irratzo), the original author of this code.

The authors acknowledge funding of the present work by the European Commission within the 
MarketPlace project (Grant ID H2020-NMBP-25-2017 760173).


## License

Copyright (c) 2019-2020, Access e.V.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
