# -*- coding: utf-8 -*-
"""

This module contains the HDF5 file reader class for the script hdf2mic.py.

Author: Johannes Wasmer, Copyright Access e.V., 2018

ChangeLog:
21-Feb-2018: Ralph Altenfeld
  group_angles:
    rotation of orientations to the MICRESS axis system

"""

import re
import h5py
import numpy as np
from hdf2mic.exceptions import Hdf2Mic_InitArgError, Hdf2Mic_HDF5DatasetNotFoundError
from hdf2mic.settings import ReaderSettings
from hdf2mic.arg_mapping import ArgMap, ArgMap_settingsInputHdf5
from hdf2mic.data import Data
from hdf2mic.rotMat import rotate


class Reader(object):
    """HDF5 file reader for script hdf2mic.py

    Parameters
    ----------
    filepath : str
        The HDF5 file path (relative or absolute)

    Attributes
    ----------

    Notes
    -----
    Use with a context manager (see example).

    Setting one of the reader's properties (HDF5 group paths) automatically reads the HDF5 dataset (in file)
    and stores it as Numpy Array (in memory) in the data attribute.

    On dataTypes: while the user specifies VTK dataTypes, the actual reading from HDF5 uses Numpy dataTypes.
    See references [1], [2], [3] as source for the used VTK -> Numpy type mapping scheme.

    Examples
    --------
    Open a file and buffer specified HDF5 datasets as Numpy arrays.

    >>> from hdf2mic.parser import Parser
    >>> parser = Parser()
    >>> params = parser.parse()
    >>> inputfile = params.MANDATORY.files.input
    >>> reader = Reader(inputfile)
    >>> with reader as h5file:
    ...     #setting param group paths reads out HDF5 datasets to reader.data
    ...     reader.dim = params.MANDATORY.other.dim
    ...     reader.group_angles = params.MANDATORY.paths.cellFeatureData.eulerAngles
    ...     #... finally:
    ...     data = reader.data

    TODO
    ----
    If the HDF5 Datasets become large, it might be more efficient to save the HDF5 Dataset (in file) to the data
    attribute rather than copy it into a Numpy array (in memory) and save that. In that case, all subsequent operations
    have to be done within the reader's context manager.

    References
    ----------
        .. [1] File formats for VTK Version 4.2.
           URL: www.vtk.org/VTK/img/file-formats.pdf
        .. [2] Microsoft Visual Studio 2015 C++ Reference, Data Type Ranges.
           URL: https://msdn.microsoft.com/de-de/library/s3f49ktz.aspx
        .. [3] Numpy v1.14 Manual User Guide Basics, Data types.
           URL: https://docs.scipy.org/doc/numpy/user/basics.types.html
    """

    def __init__(self, filepath):
        self._f_path = filepath

        self.settings = None
        self._dim = None

        # for txt file output:
        self._group_angles = None
        self._group_phases = None

        # for vtk file output:
        self._groups_celldata = None
        self._celldata_dataNames = None
        self._celldata_dataTypes = None
        self._celldata_datasetAttributeTypes = None
        self._celldata_fieldArrays = None
        self._celldata_tags = None
        self._group_dimensions = None
        self._group_origin = None
        self._group_spacing = None
        self._group_time = None

        # for both:
        self._data = Data()

        self._EXCEPTIONS_INITARG = """Tried to init reader attributes outside a with-statement.
            Instead, init reader attributes inside a with statement like this:
            reader = Hdf2Mic_FileReader()
            with reader as h5file:
            \t#initialize reader arguments..."""

    def __enter__(self):
        # trysetattr etc goes here
        self._f = h5py.File(self._f_path, 'r')
        return self._f

    def __exit__(self, type, value, traceback):
        # exception handling goes here
        self._f.close()

    def read(self, args, verbose=False):
        """
        Returns specified, preprocessed data from opened HDF5 file.

        Parameters
        ----------
        args : ArgMap

        Returns
        -------
        data : Data

        """
        assert isinstance(args, ArgMap)

        # set up reader to hdf5 input format
        # self.settings = ReaderSettings(args.settings.input.hdf5, verbose)
        self.settings = args.settings.input.hdf5
        if verbose:
            self.settings.pprint()

        # to find, read, preprocess HDF5 Datasets
        self.dim = args.data.other.dim # set first; other attribute setters depend on this
        self.group_time = args.data.other.time

        self.group_angles = args.data.paths.cellFeatureData.eulerAngles
        self.group_phases = args.data.paths.cellFeatureData.phases
        self.groups_celldata = [args.data.paths.cellData.paths,
                                args.data.paths.cellData.dataNames,
                                args.data.paths.cellData.dataTypes,
                                args.data.paths.cellData.datasetAttributeTypes,
                                args.data.paths.cellData.fieldArrays,
                                args.data.paths.cellData.tags,
                                ]
        self.group_dimensions = args.data.paths.geometry.dimensions
        self.group_origin = args.data.paths.geometry.origin
        self.group_spacing = args.data.paths.geometry.spacing

        # get the data
        return self.data

    @property
    def dim(self):
        """

        Returns
        -------
        int
            The dimensionality of the simulation: 1, 2, or 3.

        Notes
        -----
        Setter also sets corresponding attribute in reader's attribute `data`.
        """
        return self._dim

    @dim.setter
    def dim(self, value):
        assert isinstance(value, int)
        if not value in [1, 2, 3]:
            raise Hdf2Mic_InitArgError("Reader: dimension 'dim' not in (1, 2 or 3).")
        self._dim = value
        self.data._dim = self._dim

    @property
    def group_angles(self):
        """

        Returns
        -------
        str
            HDF5 group path.

        Notes
        -----
        Property `dim` has to be set in advance!

        Setter also locates Dataset in HDF5 file and copies it into reader's attribute `data`.
        """
        return self._group_angles

    @group_angles.setter
    def group_angles(self, value):
        try:
            self._group_angles = value
            dset = self.dset(self.group_angles, safe=True)
            angles = None
            if dset is not None:
                if self.dim == 2:
                    angles = dset[..., 0]
                    # Clips 2nd and 3rd column of angle=[phi, theta, psi].
                    # Example for six grains: shape (6L, 3L) --> (6L, 1L).
                    # Result in output: only one value per grain instead of three.
                    # Reason for this:
                    # If dim==2, this assumes angle == [phi,theta,psi] == [  x,  0,  0].
                    # If user wants all values, she can always set dim=3.
                    # Then rotate( [x,0,0] ) yields newAngle ==           [270,  x, 90].
                elif self.dim == 3:
                    angles = dset[...]
                if len(angles.shape) == 1:
                    angles = angles.reshape((-1, 1))

                if self.settings.cellFeatureDataClipFirstLine:
                    if len(angles.shape) > 1:
                        angles = angles[1:, :]

            newAngles = angles

            # YB TODO: this section has been skipped bugs to be fixed!!! 
            # YB here you only initialize the data array!! 
            if (self.settings.rotate and self.dim == 30):
                # RA: rotation of euler angles is necessary
                # MICRESS is using a special axis definition for its coordinate system.
                # Typically this is not the common one.
                # We need to parameterize this!
                # TODO: make data type handling more elegant
                for i in range(angles.shape[0]):
                    val = []
                    for j in range(angles.shape[1]):
                        val.append(angles[i][j])
                    rotVal = rotate(val, True)
                    for j in range(angles.shape[1]):
                        newAngles[i][j] = rotVal[j]
            self.data.angles = newAngles
        except AttributeError:
            raise Hdf2Mic_InitArgError(self._EXCEPTIONS_INITARG)

    @property
    def group_phases(self):
        """

        Returns
        -------
        str
            HDF5 group path.

        Notes
        -----
        Property `dim` has to be set in advance!

        Setter also locates Dataset in HDF5 file and copies it into reader's attribute `data`.
        """
        return self._group_phases

    @group_phases.setter
    def group_phases(self, value):
        try:
            self._group_phases = value
            dset = self.dset(self._group_phases, safe=True)
            phases = None
            if dset is not None:
                phases = dset[...]
                if len(phases.shape) == 1:
                    # transform row -> column for comparing with angles
                    phases = phases.reshape((-1, 1))

            if self.settings.cellFeatureDataClipFirstLine:
                if len(phases.shape) > 1:
                    phases = phases[1:, :]

            self.data.phases = phases
        except AttributeError:
            raise Hdf2Mic_InitArgError(self._EXCEPTIONS_INITARG)

    @property
    def groups_celldata(self):
        """

        Returns
        -------
        str
            HDF5 group path.

        Notes
        -----
        Setter expects argument to be list of 6 lists:
          - HDF5 paths
          - VTK dataNames
          - VTK dataTypes
          - VTK datasetAttributeTypes
          - VTK fieldArrays
          - VTK tags
        These lists are checked for the following conditions (excerpt):
          - the first 4 lists must be of equal length.
          - the fifth list's length must correspond to the number of 'FIELD' elements
            in the  fourth list

        Setter also locates Dataset in HDF5 file and copies it into reader's attribute `data`.

        Alternative implementation: define the dataName and dataType for each array (HDF5
        Dataset value) as optional. Then when they are not specified in the JSON, this method
        would use the HDF5 Dataset's name as dataName and dataType would default to float.
        """
        return self._groups_celldata

    @groups_celldata.setter
    def groups_celldata(self, values):
        # check input arguments
        if not isinstance(values, list):
            raise Hdf2Mic_InitArgError(
                "Reader: CellData input is not a list [paths, dataNames, dataTypes, datasetAttributeTypes, fieldArrays, tags].")
        if not all(isinstance(li, list) for li in values) or not (len(values) == 6):
            raise Hdf2Mic_InitArgError(
                "Reader: CellData input is not a list of 6 lists [paths, dataNames, dataTypes, datasetAttributeTypes, fieldArrays, tags].")
        if not all(isinstance(el, str) for li in values for el in li):
            raise Hdf2Mic_InitArgError("Reader: CellData input lists are not lists of strings.")
        val_it = iter(values[:4])
        val_len = len(next(val_it))
        if not all(len(li) == val_len for li in val_it):
            raise Hdf2Mic_InitArgError(
                "Reader: CellData input first four lists are not equally long [paths, names, types, datasetAttributes].")
        if not all([el in self.data.VTK_TYPE_MAP_VTK_TO_NUMPY[int].keys() or el in
                    self.data.VTK_TYPE_MAP_VTK_TO_NUMPY[
                        float].keys() for el in values[2]]):
            raise Hdf2Mic_InitArgError(
                "Reader: CellData input list 'dataTypes' has unknown VTK dataTypes. See comment in JSON template for accepted dataTypes.")
        if not all([el in self.data.VTK_DATASET_ATTRIBUTE_TYPE_ORDER.keys() for el in values[3]]):
            raise Hdf2Mic_InitArgError(
                "Reader: CellData input list 'datasetAttributeTypes' has unknown VTK Dataset Atrribute Types. See comment in JSON template for accepted types.")

        # check input arguments: fieldArrays
        regex_fieldArrays = re.compile('([^\s]+)(\s+)(\d+)')
        if not all([regex_fieldArrays.match(el) is not None for el in values[4]]):
            raise Hdf2Mic_InitArgError(
                "Reader: CellData input fifth list 'fieldArrays' is not a list of strings of type 'arrName numComp' where arrName type is String and numComp type is integer.")
        count_field_arrays = sum([el == 'FIELD' for el in values[3]])
        if count_field_arrays > len(values[4]):
            # in case there -IS- a FIELD specified but -NOT- a FIELD array specified
            raise Hdf2Mic_InitArgError(
                "Reader: CellData input: number of FIELDs ={} does not match number of fieldArrays ={}."
                    .format(count_field_arrays, len(values[4])))

        # convert fieldArray strings to tuples (arrayName str, numComponents int)
        # IF a FIELD is specified AND the FIELD arrays are not empty or default
        fieldArrays = None
        if count_field_arrays:
            # if count_field_arrays and and not (not values[4][0] or values[4][0] == 'unnamed 0'):
            fieldArrays = [(regex_fieldArrays.match(el).group(1),
                            int(regex_fieldArrays.match(el).group(3))) for el in values[4]]

        # check input arguments: tags
        regex_tags = re.compile('<.*>')
        if not all([(not el.strip()) or (regex_tags.match(el.strip()) is not None) for el in values[5]]):
            raise Hdf2Mic_InitArgError(
                "Reader: CellData input sixth list 'tags' is not a list of strings that are empty or of type '<mytagname>'.")
        # pad tags list if too short
        values[5] += [''] * (val_len - len(values[5]))

        # process input arguments
        self._groups_celldata = values[0]
        self._celldata_dataNames = values[1]
        self._celldata_dataTypes = values[2]
        self._celldata_datasetAttributeTypes = values[3]
        self._celldata_fieldArrays = fieldArrays
        self._celldata_tags = values[5]

        # read data arrays from HDF5 file
        celldata_arrays = []
        for i in range(len(self.groups_celldata)):
            celldata_path = self._groups_celldata[i]
            celldata_name = self._celldata_dataNames[i]
            celldata_type = self._celldata_dataTypes[i]
            print("reader: groups_celldata setter: reading dset of dataName: {}".format(celldata_name))

            dset = self.dset(celldata_path)  # h5py.Dataset
            try:
                numpy_type = self.data.numpy_type_for_vtk_type(celldata_type)
                with dset.astype(numpy_type):
                    celldata_array = dset[...]  # np.ndarray
                    if len(celldata_array.shape) == 1:
                        celldata_array = celldata_array.reshape((-1, 1))
                        
                    rotArray = np.ndarray(shape=celldata_array.shape, dtype=numpy_type)
                    if(self.settings.rotate and celldata_name == "euler"):
                        x,y,z = celldata_array.shape # z immer 3!!!
                        for xx in range (x):
                            for yy in range (y):
                                try:
                                    ttt = rotate([celldata_array[xx][yy][0],celldata_array[xx][yy][1],celldata_array[xx][yy][2]],True)
                                    rotArray[xx,yy,0]= ttt[0]
                                    rotArray[xx,yy,1]= ttt[1]
                                    rotArray[xx,yy,2]= ttt[2]
#                                    print (celldata_array[xx][yy])
                                except ValueError as err:
                                    print("celldata_scalar[x][y][z] = {}".format(celldata_array[xx][yy]))
                                    raise err
                        celldata_array = rotArray
                        

                    # YB TODO: this section has been skipped; bugs to be fixed!!! 
                    if (self.settings.rotate and self.dim == 30 and celldata_name == "euler"):
                        # RA: Hack to reorder array elements, necessary for rotated axis system
                        # YW TODO: elegantere Moeglichkeit? Warum ist 'array' andersherum angeordnet (z,y,x) ?
                        # JW TODO: this swap method is really inefficient. Try h5py method on dset (slicing?) or else numpy.
                        (dimZ, dimY, dimX, t) = celldata_array.shape
                        rotArray = None
#                        if (t == 1):
#                            rotArray = np.ndarray(shape=(dimY, dimZ, dimX), dtype=numpy_type)
#                        elif (t > 1):
#                            rotArray = np.ndarray(shape=(dimY, dimZ, dimX, t), dtype=numpy_type)
                        rotArray = np.ndarray(shape=(dimY, dimZ, dimX, t), dtype=numpy_type)
                        for z in range(dimZ):
                            for y in range(dimY):
                                for x in range(dimX):
                                    try:
                                        cellValue = celldata_array[z][y][x]

                                        # check if this cellData has to rotated locally as well
                                        # (e.g. cell-wise eulerAngles)
                                        cellDataToRotate = self.settings.rotateCellDataValues
                                        if cellDataToRotate is not None and cellDataToRotate:  # non-empty list
                                            # if int, compare to loop index. if str, compare to dataName
                                            if (any((el == i or el == celldata_name) for el in cellDataToRotate)):
                                                cellValue = rotate(cellValue, True)
                                                # JW: is this correct???

                                        rotArray[dimY - y - 1][z][x] = cellValue
                                    except ValueError as err:
                                        print("celldata_scalar[z][y][x] = {}".format(celldata_array[z][y][x]))
                                        raise err
                        celldata_array = rotArray
                        
                    celldata_arrays.append(celldata_array)

            except (KeyError, TypeError) as error:
                print("ERROR: Unknown VTK dataType {} for cellData with path {}. See JSON template for accepted types."
                    .format(celldata_type, celldata_path))
                raise error

        # transform to one tuple list (array,dataName,dataType,dsetAttributeType) for each array
        tuples = zip(celldata_arrays,
                     self._celldata_dataNames,
                     self._celldata_dataTypes,
                     self._celldata_datasetAttributeTypes)
        # sort in-place by DatasetAttributeType
        tuples.sort(key=lambda tup: self.data.VTK_DATASET_ATTRIBUTE_TYPE_ORDER[tup[3]])

        # append fieldArray list
        if count_field_arrays:
            # sort FIELDs at end of list by dataName
            count_non_field_arrays = len(tuples) - count_field_arrays
            field_tuples = tuples[-count_field_arrays:]
            field_tuples.sort(key=lambda tup: tup[1])
            tuples = tuples[:-count_field_arrays] + field_tuples
            # append fieldArray name and fieldArray numTuples to FIELD tuples
            for i in range(count_non_field_arrays, len(tuples)):
                tuples[i] = tuples[i] + self._celldata_fieldArrays[i - count_non_field_arrays]

        # append tags
        for i in range(len(tuples)):
            tuples[i] = tuples[i] + (self._celldata_tags[i],)

        self.data.celldata = tuples

    @property
    def group_dimensions(self):
        """

        Returns
        -------
        str
            HDF5 group path.

        Notes
        -----
        Setter also locates Dataset in HDF5 file and copies it into reader's attribute `data`.
        Also sets the latter's attribute `cell_data`.

        Converts original x,y,z dimensions from VtkCell to VtkPoint format: dim_i --> dim_i + 1.
        `cell_data`is then computed as prod( dim_i).
        """
        return self._group_dimensions

    @group_dimensions.setter
    def group_dimensions(self, value):
        self._group_dimensions = value
        dimensions_vtkCell = self.dset(self.group_dimensions)[...]
        dimensions_vtkPoint = np.array([d + 1 for d in dimensions_vtkCell])

        self.data._celldata_size = np.product(dimensions_vtkCell)

        if (self.settings.rotate and self.dim == 3):
            # RA: Hack to rotate results: exchange y and z dimensions
            self.data.dimensions = [dimensions_vtkPoint[0], dimensions_vtkPoint[2], dimensions_vtkPoint[1]]
        else:
            self.data.dimensions = dimensions_vtkPoint

    @property
    def group_origin(self):
        """

        Returns
        -------
        str
            HDF5 group path.

        Notes
        -----
        Setter also locates Dataset in HDF5 file and copies it into reader's attribute `data`.
        """
        return self._group_origin

    @group_origin.setter
    def group_origin(self, value):
        self._group_origin = value
        origin = self.dset(self.group_origin)[...]
        self.data.origin = origin

    @property
    def group_spacing(self):
        """

        Returns
        -------
        str
            HDF5 group path.

        Notes
        -----
        Setter also locates Dataset in HDF5 file and copies it into reader's attribute `data`.
        """
        return self._group_spacing

    @group_spacing.setter
    def group_spacing(self, value):
        self._group_spacing = value
        spacing = self.dset(self.group_spacing)[...]
        self.data.spacing = spacing

    @property
    def group_time(self):
        """

        Returns
        -------
        str
            HDF5 group path, or time value as str

        Notes
        -----
        Setter also locates Dataset in HDF5 file and copies it into reader's attribute `data`.
        Since time is an OPTIONAL conversion parameter, only a WARNING is issued if the Dataset is not found.
        """
        return self._group_time

    @group_time.setter
    def group_time(self, value):
        self._group_time = value

        number = self.is_number(s=self.group_time)
        if number is not None:
            self.data.time = number
        elif self.group_time.startswith("/"):
            time = self.dset(self.group_time, safe=True)
            if time is not None and np.isscalar(time.value[0]):
                self.data.time = time.value[0]
            else:
                print('WARNING: could not find time value at specified HDF5 group path {}'
                    .format(self.group_time))
                self.data.time = None

    @property
    def data(self):
        """

        Returns
        -------
        Data
            All of the reader's set group path's HDF5 Dataset as Numpy arrays.

        Notes
        -----
        Read-only.
        """
        return self._data

    @data.setter
    def data(self, value):
        pass

    def dset(self, h5path, safe=False):
        """

        Parameters
        ----------
        h5path : str
            HDF5 group path in file.

        Returns
        -------
        Dataset
            h5py.Dataset

        Raises
        ------
        Hdf2Mic_HDF5DatasetNotFoundError
            if file has no such Dataset
        """
        if h5path == '/' or h5path == '':
            if safe:
                return None
            else:
                pass

        dset = self._f.get(h5path)
        if dset is not None:
            return dset
        elif not safe:
            raise Hdf2Mic_HDF5DatasetNotFoundError('ERROR: HDF5 input file {} has no Dataset at {}. Aborting.'
                                                   .format(self._f.filename, h5path))
        return None

    def is_number(self, s):
        try:
            return float(s)
        except ValueError:
            return None
