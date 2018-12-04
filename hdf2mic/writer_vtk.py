# -*- coding: utf-8 -*-
r"""

This module contains the MICRESS input ASCII VTK file writer for the script hdf2mic.py.
"""

import numpy as np
from hdf2mic.exceptions import *
from hdf2mic.writer import *
from hdf2mic.data import Data
from hdf2mic.arg_mapping import ArgMap_settingsOutputVtk
#from deprecated import deprecated


class VtkWriter(Writer):
    """

    Writes Numpy Arrays of EulerAngles and Phases to MICRESS input ASCII VTK.

    Notes
    -----
    Use with a context manager (see example).

    Examples
    --------
    Write to file.

    >>> #...
    >>> data = reader.data
    >>> writer = VtkWriter(ouputfile_vtk)
    >>> with writer as f:
    ...     writer.write(data)
    """

    def __init__(self, filepath):
        Writer.__init__(self, filepath)

        self._HEADER_TEMPLATE = """# vtk DataFile Version {vtk_version}
{vtk_title_time}
ASCII
DATASET STRUCTURED_POINTS
DIMENSIONS {dim}
SPACING {spc}
ORIGIN {orig}
CELL_DATA {cell}
"""

        self._SCALARS_TEMPLATE = """SCALARS {data_name} {data_type}
LOOKUP_TABLE default"""

        self._DATASET_ATTRIBUTE_TEMPLATES = {
            'SCALARS': """SCALARS {data_name} {data_type}
LOOKUP_TABLE default""",
            'VECTORS': """VECTORS {data_name} {data_type}""",
            'NORMALS': """NORMALS {data_name} {data_type}""",
            'TENSORS': """TENSORS {data_name} {data_type}""",
            'FIELD': ["""FIELD {data_name} {num_arrays}""",
                      """{array_name} {num_components} {num_tuples} {data_type}"""],
        }

    def write(self, data, settings, verbose):
        """

        Parameters
        ----------
        data : Data
        settings : ArgMap_settingsOutputVtk
        verbose : bool

        Raises
        ------
        AttributeError
             If not called inside a context manager.
        """
        super(VtkWriter, self).write(data, settings, verbose)

        # check that writer and data DatasetAttributeType key-sets match
        if not self._DATASET_ATTRIBUTE_TEMPLATES.keys() == data.VTK_DATASET_ATTRIBUTE_TYPE_ORDER.keys():
            raise TypeError(
                "ERROR: vtk_writer: writer DatasetAttributeType key-set {} does not match data DatasetAttributeType key-set {}"
                    .format(self._DATASET_ATTRIBUTE_TEMPLATES.keys(),
                            data.VTK_DATASET_ATTRIBUTE_TYPE_ORDER.keys()))

        try:
            # arguments from HDF5 file:
            s_dim = ' '.join(map(str, data.dimensions))
            s_spacing = ' '.join(map(str, data.spacing))
            s_origin = ' '.join(map(str, data.origin))
            s_title = 't=? s'
            if data.time is not None:
                s_title = s_title.replace('?', '{:.5f}'.format(data.time))

            # arguments from user:
            s_version = '{:.1f}'.format(self.settings.version)

            # write VTK 'header'
            header = self._HEADER_TEMPLATE.format(
                vtk_version=s_version,
                vtk_title_time=s_title,
                dim=s_dim, spc=s_spacing, orig=s_origin,
                cell=data.celldata_size)
            self._f.write(header)

            # write CellData: all except FIELDs:
            # NOTE: assumes that tuples sorted by data DatasetAttributeType order
            # (FIELD arrays is penultimate element before tags),
            # AND that VTK FIELD arrays are sorted according to VTK FIELD.
            for tupl in data.celldata:
                array = tupl[0]
                dataName = tupl[1]
                dataType = tupl[2]
                datasetAttributeType = tupl[3]

                if datasetAttributeType == 'FIELD':
                    break
                else:
                    header = self._DATASET_ATTRIBUTE_TEMPLATES[datasetAttributeType] \
                        .format(data_name=dataName, data_type=dataType)
                    # write cellData
                    self._write_array(header, dataType, array)

            # write CellData: FIELDs
            # NOTE: assumes that tuples sorted by data DatasetAttributeType order
            # (FIELD arrays is penultimate element before tags),
            # AND that VTK FIELD arrays are sorted according to VTK FIELD.
            count_non_field_tuples = sum([tup[3] != 'FIELD' for tup in data.celldata])
            if count_non_field_tuples < len(data.celldata):
                datasetAttributeType = data.celldata[count_non_field_tuples][3]
                if datasetAttributeType != 'FIELD':
                    raise TypeError(
                        "vtk_writer: Expected CellData tuple {} to be 'FIELD' according to Data DatasetAttributeType"
                        " sorting order, but was {}.".format(count_non_field_tuples, datasetAttributeType))
                if not all(len(tup) == 7 for tup in data.celldata[count_non_field_tuples:]):
                    for dsat in data.celldata[count_non_field_tuples:]:
                        print("{} -- len: ".format(', '.join(map(str, dsat[1:]))), len(dsat))
                    raise TypeError(
                        "vtk_writer: Expected CellData tuple {} and all following to be 'FIELD's according to "
                        "Data DatasetAttributeTyp sorting order, each tuple having six elements "
                        "(array, dataName, dataType, datasetAttributeType, arrayName, numTuples), but found other "
                        "number of elements.".format(count_non_field_tuples))

                header_field = self._DATASET_ATTRIBUTE_TEMPLATES[datasetAttributeType][0]

                # For each FIELD, write FIELD header, then each associated FIELD array.
                # First, get unique FIELD dataNames
                field_dataNames = [el[1] for el in data.celldata[count_non_field_tuples:]]
                field_dataNames = list(sorted(set(field_dataNames)))

                for dataName in field_dataNames:

                    # get FIELD array tuples
                    tuples = [el for el in data.celldata[count_non_field_tuples:] if el[1] == dataName]

                    # write FIELD header
                    numArrays = len(tuples)
                    header_field = header_field.format(data_name=dataName, num_arrays=numArrays)
                    self._f.close()
                    self._f = open(self._f_path, 'a')
                    self._f.write(header_field + '\n')

                    # write FIELD arrays
                    for tuple in tuples:
                        # write FIELD array header
                        header_array = self._DATASET_ATTRIBUTE_TEMPLATES[datasetAttributeType][1]
                        # get header_array format arguments
                        array = tuple[0]
                        arrayName = tuple[4]
                        numComponents = tuple[5]
                        numTuples = tuple[0].size / numComponents
                        dataType = tuple[2]
                        header_array = header_array.format(
                            array_name=arrayName, num_components=numComponents,
                            num_tuples=numTuples, data_type=dataType
                        )

                        self._write_array(header_array, dataType, array)

        except AttributeError as error:
            # raise Hdf2Mic_InitArgError(self._EXCEPTIONS_INITARG)
            raise error

    def _write_array(self, header, dataType, array):

        size = array.size
        divisor = size / self.settings.columns
        remainder = size % self.settings.columns
        divisor_quotient = size - remainder
        bulk = array.flat[:divisor_quotient].reshape(divisor, self.settings.columns)
        tail = array.flat[divisor_quotient:]
        if dataType in Data.VTK_TYPE_MAP_VTK_TO_NUMPY[int]:
            fmt = "%u"
        else:
            fmt = "%f"
        self._f.close()
        self._f = open(self._f_path, 'a')
        np.savetxt(self._f, bulk, fmt=fmt, delimiter=' ', header=header, comments='')
        if remainder > 0:
            np.savetxt(self._f, tail, fmt=fmt, newline=' ')
            self._f.write('\n')

#    @deprecated(reason="Use write(data) instead (Approx. 2x faster)")
    def write_DEPRECATED(self, data, vtkFormat):
        try:
            s_dim = ' '.join(map(str, data.dimensions))
            s_spacing = ' '.join(map(str, data.spacing))
            s_origin = ' '.join(map(str, data.origin))
            s_name = self.header_scalars_dataname

            header = self._HEADER_TEMPLATE.format(
                dim=s_dim, spc=s_spacing, orig=s_origin,
                cell=data.cell_data, name=s_name)

            # write header - old write(data) needs another newline here:
            self._f.write(header + '\n')

            # write featureids (SCALAR lookup_table):
            row = []
            count = 0
            size = data.celldata.size
            for x in np.nditer(data.celldata):
                row.append(x)
                count += 1
                if (len(row) == vtkFormat.scalars_columns) or (size == count):
                    s_row = ' '.join(map(str, row)) + '\n'
                    self._f.write(s_row)
                    row = []

        except AttributeError:
            raise Hdf2Mic_InitArgError(self._EXCEPTIONS_INITARG)
