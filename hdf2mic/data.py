# -*- coding: utf-8 -*-
r"""

This module contains classes the class that can exchange HDF5 Datasets for the script hdf2mic.py.
"""

import numpy as np
from hdf2mic.exceptions import Hdf2Mic_HDF5DatasetDimensionError


class CellData(object):
    def __init__(self):
        self.data = np.empty(())
        self.name = 'unnamed'
        self.type = 'unknown'


class Data(object):
    """

    Holds the data read from HDF5 file.

    Notes
    -----
    The values are set indirectly via the hdf2mic.py reader. As noted there, Numpy Arrays (in memory) are stored instead
    of the h5py.Dataset handles (in file) for easier processing.

    Attributes
    ----------
    _dim : int
        The HDF5 data's dimension: 1,2 or 3. User-defined, NOT read from HDF5.
    angles : numpy.ndarray
        EulerAngles from HDF5
    phases : numpy.ndarray
        Phases from HDF5
    grain_count : int
        Calculated indirectly
    feature_ids : numpy.ndarray
        cell / field scalar field data, usually grainID per cell from HDF5
    dimensions : numpy.ndarray
        3x1 array, cells per dimension from HDF5
    _celldata_size : int
        number of cells, calculated indirectly
    origin : numpy.ndarray
        3x1 array, origin from HDF5
    spacing : numpy.ndarray
        3x1 array, cell spacing



    """
    DRI_TAG_GRAIN_PROPERTIES = "<grain-properties>"
    DRI_TAG_PHASES = "<distinct-phases>" #added in v0.4, deactivated in v0.5 by request RA
    DRI_TAG_CELLS = ["<cellsX>", "<cellsY>", "<cellsZ>", ]
    DRI_TAG_SPACING = "<spacing>"

    VTK_TYPE_MAP_VTK_TO_NUMPY = {
        int: {
            'bit': 'uint8',
            'unsigned_char': 'uint8',
            'char': 'int8',
            'unsigned_short': 'uint16',
            'short': 'int16',
            'unsigned_int': 'uint32',
            'int': 'int32',
            'unsigned_long': 'uint64',
            'long': 'int64'},
        float: {
            'float': 'float32',
            'double': 'float64'}
    }

    VTK_DATASET_ATTRIBUTE_TYPE_ORDER = {
        'SCALARS': 0, 'VECTORS': 1, 'NORMALS': 2, 'TENSORS': 3, 'FIELD': 4
    }

    def numpy_type_for_vtk_type(self, vtk_type):
        if vtk_type in self.VTK_TYPE_MAP_VTK_TO_NUMPY[int]:
            return self.VTK_TYPE_MAP_VTK_TO_NUMPY[int][vtk_type]
        elif vtk_type in self.VTK_TYPE_MAP_VTK_TO_NUMPY[float]:
            return self.VTK_TYPE_MAP_VTK_TO_NUMPY[float][vtk_type]
        else:
            raise TypeError("ERROR: Unknown VTK dataType {}.".format(vtk_type))

    def __init__(self):
        self._dim = None
        self._angles = None
        self._phases = None
        self._grain_count = None

        self._celldata = None
        self.dimensions = None
        self._celldata_size = None
        self._origin = None
        self._spacing = None

        self.time = None

    @property
    def dim(self):
        return self._dim

    @dim.setter
    def dim(self, value):
        if value not in [1, 2, 3]:
            raise Hdf2Mic_HDF5DatasetDimensionError("User-specified 'dim' is {} and not 1, 2 or 3.".format(value))
        self._dim = value

    @property
    def angles(self):
        return self._angles

    @angles.setter
    def angles(self, value):
        self._angles = value
        if isinstance(self.angles, np.ndarray):
            self._grain_count = self.angles.shape[0]
        self._compare_angles_phases()

    @property
    def phases(self):
        return self._phases

    @phases.setter
    def phases(self, value):
        self._phases = value
        if isinstance(self.phases, np.ndarray):
            self._grain_count = self.phases.shape[0]
        self._compare_angles_phases()

    @property
    def celldata(self):
        return self._celldata

    @celldata.setter
    def celldata(self, tuples):
        if not isinstance(tuples, list):
            raise TypeError("Data: cellData is not a list.")
        if not all(isinstance(tup, tuple) for tup in tuples):
            raise TypeError("Data: cellData input list elements are not all tuples.")
        if not all(isinstance(tup[0], np.ndarray) for tup in tuples):
            raise TypeError("Data: cellData input list tuples first elements are not all numpy arrays.")
        if not all(len(tup) in [5, 7] for tup in iter(tuples)):
            raise ValueError("Data: cellData input list tuples lengths are not all 5 or 7:"
                             "(path, dataName, dataType, datasetAttributeType, [fieldArray name, fieldArray numComponents,] tag).")

        celldata_scalars = []
        for tupl in tuples:
            if self._check_array_dimensionality(tupl):
                celldata_scalars.append(tupl)
            else:
                # Examples:
                # 2D: `x=200,y=1,z=200`   -> (200L,   1L, 200L, 1L) -> 2 == 4 - 2
                # 3D: `x=128,y=128,z=128` -> (128L, 128L, 128L, 1L) -> 1 == 4 - 3
                raise Hdf2Mic_HDF5DatasetDimensionError("""User-specified data dimension 'dim' ={} 
                                           does not fit cellData dimensions ={} for cellData with name '{}'"""
                                                        .format(self._dim, tupl[0].shape, tupl[1]))

        self._celldata = celldata_scalars

    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, value):
        self._origin = self._convert2int_if_no_decimals(value)
        # self._origin = value

    @property
    def spacing(self):
        """

        An arrray of identical numbers (see setter: MICRESS only allows cubic cells).

        If all numbers are integers, converted to integer array for ASCII VTK output.

        Returns
        -------
        numpy.ndarray

        """
        return self._spacing

    @spacing.setter
    def spacing(self, value):
        if not all(value == value[0]):
            raise ValueError("Data: spacing input list {} implies non-cubic cells. MICRESS only supports cubic cells."
                             .format(value))
        self._spacing = self._convert2int_if_no_decimals(value)

    @property
    def celldata_size(self):
        return self._celldata_size

    @celldata_size.setter
    def celldata_size(self, value):
        self._celldata_size = value

        # TODO:
        # check against celldata
        # if self._celldata is not None:
        # check against each celldata array dim:
        # take each arr's shape and discard numbers for it's type (for SCALAR: the 1's, for VECTOR: the 3's,...)
        # product of the result should match celldata_size, else ValueError.

    @property
    def grain_count(self):
        return self._grain_count

    @grain_count.setter
    def grain_count(self, value):
        """Set indirectly via setting angles and phases."""
        pass

    def _has_equal_dimensions(self, a, b):
        """

        Parameters
        ----------
        a : numpy.ndarray
        b : numpy.ndarray

        Returns
        -------
        bool
            True if every column has same length and same number of columns
        """
        try:
            dims_no_a = len(a.shape)
            dims_no_b = len(b.shape)
            if dims_no_a != dims_no_b:
                return False
            elif np.prod(a.shape) != np.prod(b.shape):
                return False
            else:
                # [i for i, j in zip(a, b) if i == j]
                index = 0
                for idim in a.shape:
                    jdim = b.shape[index]
                    if idim != jdim:
                        return False
                    index += 1
                return True
        except AttributeError:
            raise Hdf2Mic_HDF5DatasetDimensionError

    def _compare_angles_phases(self):
        """

        Checks if angles and phases has same number of grains (rows).

        """
        if isinstance(self.angles, np.ndarray) and isinstance(self.phases, np.ndarray):
            for i in range(self.angles.shape[1]):
                if not self._has_equal_dimensions(self.angles[:, i], self.phases[:, 0]):
                    raise Hdf2Mic_HDF5DatasetDimensionError("Data: dim mismatch between angles {} and phases {}"
                                                            .format(self.angles[:, i], self.phases[:, 0]))

    def _convert2int_if_no_decimals(self, arr):
        arr_copy = np.copy(arr)
        np.mod(arr_copy, 1, out=arr_copy)
        is_whole_number = (arr_copy == 0)
        if all(is_whole_number):
            return arr.astype(int)
        else:
            return arr

    def _check_array_dimensionality(self, celldata_tuple):
        return True
        # raise Error("ERROR: Data: method _check_array_dimensionality not implemented yet!")

        # TODO:
        # check that user-specified 'dim' matches
        # array shape. Example:
        # tuple is SCALAR -> count no. of ones
        # 1D: (128,1,1,1) --> 3
        #     (    4 - 'dim') = 2 --> return True
        # 3D: (128,128,128,1) --> 1
        #     (    4 - 'dim') = 3 --> return True
        # tuple is VECTOR -> count no. of threes
        # tuple is FIELD -> count no. of 'numTuples' (tup[5])
        # ...

        # array = celldata_tuple[0]
