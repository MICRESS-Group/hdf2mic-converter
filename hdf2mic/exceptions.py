# -*- coding: utf-8 -*-
r"""

This module contains all special exceptions/errors for the script hdf2mic.py.
"""

class Hdf2Mic_Exception(Exception):
    """Generic exception for hdf2mic"""
    pass

class Hdf2Mic_InitArgError(Hdf2Mic_Exception):
    """Raised when reader attributes are set without a context manager"""
    pass

class Hdf2Mic_HDF5DatasetDimensionError(Hdf2Mic_Exception):
    """
    Raised when a read HDF5 Dataset's dimension conflicts present data
    Example: EulerAngles and Phases have differing length
    """
    pass

class Hdf2Mic_HDF5DatasetNotFoundError(Hdf2Mic_Exception):
    """
    Raised when a group path for a Dataset in a HDF5 file returns
    None (i.e., the file has no such Dataset)
    """

class Hdf2Mic_DrivingFileTaggingError(Hdf2Mic_Exception):
    """
    Raised when a driving template file should be processed,
    but required tags are not specified.
    """