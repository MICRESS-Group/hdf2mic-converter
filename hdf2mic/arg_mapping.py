# -*- coding: utf-8 -*-
r"""

This module contains classes for mapping the input to the hdf2mic script, a JSON file holding the conversion parameters,
into a typed Python object instead of a simple dictionary. Main reason: enabling Tab-completion in IDEs / Notebooks.

References
----------
    .. [1] Sean Johnsen, "Deserializing nested dictionaries into complex, typed(!) python objects",
       URL: http://www.seanjohnsen.com/2016/11/23/pydeserialization.html

"""

import json
from hdf2mic.data import Data




class ArgMapper(object):
    r"""ArgMapper description

    Provides a mapping between JSON input of conversion parameters and deserialized parameters as a typed object (ArgMap)
    instead of a dictionary. Such classes must extend this class.

    Parameters
    ----------
    kwargs : dict
        deserialized JSON file (dictionary)

    Attributes
    ----------
    TEMPLATE_JSON : dict
        master template for JSON conversion file for serialization. Must match structure of ArgMap class.
    _fields : list
        in derived class: holds tuples of (key-name (str), value-type (type)) for JSON key-value pairs
    _COMMENT : str
        standard key-name for comment kv-pairs (ignored)


    Examples
    --------
    Deserialize a (valid) JSON conversion file.

    >>> import json
    >>> from hdf2mic.parser import Parser
    >>> parser = Parser()
    >>> with open(jsonfile, 'r') as json_data:
    ...     json_dict = json.load(json_data)
    ...     json_dict = parser.byteify(json_dict)
    >>> conversion_params = ArgMap(**json_dict)
    >>> print(type(conversion_params))
    # <type ArgMap>

    Notes
    -----
    In v0.4, dri tag <distinct-phases> was added.
    Was removed in v0.5 again as per request by RA.
    Saving the JSON_TEMPLATE entry here in case the
    tag is needed again in future versions.
    Insertion place: data/files/_comment
                    "  - " + Data.INPUT_DRI_TAG_PHASES,
                    "    mapping 'MANDATORY' > 'paths' > 'cellFeatureData' > 'phases' (count distinct)",
                    "    to dri file's phase data > no. of distinct solid phases.",


    """

    _fields = []
    _COMMENT = '_comment'
    JSON_TEMPLATE = {
        "_comment": [
            "=============================================================",
            "========== Input file for the Python script hdf2mic =========",
            "================== Template version: 0.5 ====================",
            "- Usage:",
            "  - Name this file like the HDF5 input file, e.g. my_sim.json.",
            "  - Fill in values:",
            "    - Default format: (STRING). Exceptions specified in comments.",
            "    - Do not remove keys for empty / unused values.",
            "  - Run $ hdf2mic convert my_sim.json",
            "       ($ python hdf2mic.py, if not installed as package).",
            " ------------------------------------------------------------",
            " Developer Notes:",
            " - if structure is changed, update hdf2mic's mapping classes.",
            "============================================================="
        ],
        "data": {
            "files": {
                "_comment": [
                    "---------------------------------------------",
                    "If a file should not be read/written, leave default",
                    "values or empty.",
                    "---------------------------------------------",
                    "'dri_template': A MICRESS driving file template",
                    "may be supplied. This template may contain a subset",
                    "of the identifier tags of the format '<mytagname>' ",
                    "from the following list. hdf2mic will replace each tag",
                    "as specified here.",
                    "1. Template may contain tag(s)",
                    "  - " + ", ".join(map(str, Data.DRI_TAG_CELLS)) + " (first 1, 2 or 3 according to dim)",
                    "    mapping 'MANDATORY' > 'paths' > 'geometry' > 'dimensions'",
                    "    to dri file's geometry > grid size.",
                    "  - " + Data.DRI_TAG_SPACING,
                    "    mapping 'MANDATORY' > 'paths' > 'geometry' > 'spacing'.",
                    "    to dri file's geometry > cell dimension.",
                    "2. If 'output' > 'txt' file is defined, template *must* contain tag(s)",
                    "  - " + Data.DRI_TAG_GRAIN_PROPERTIES,
                    "    for the driving file's grain input > grain properties.",
                    "3. If 'output' > 'vtk' file is defined, template may contain tag(s)",
                    "  - that are user-defined",
                    "    mapping data 'MANDATORY' > 'paths' > 'cellData'.",
                    "    to dri file references to data in the VTK output file.",
                    "    See 'cellData' > '_comment' for how to define these tags.",
                    "---------------------------------------------",
                ],
                "input": {
                    "hdf5": ".dream3d",
                    "dri_template": ".txt"
                },
                "output": {
                    "dri": ".txt",
                    "txt": ".txt",
                    "vtk": ".vtk"
                }
            },
            "other": {
                "_comment": [
                    "---------------------------------------------",
                    "dim (INTEGER):",
                    "Means: is the data 1D, 2D or 3D.",
                    "Default: 0 (no conversion). Accepted values:",
                    "2 or 3. Do not confuse with key -dimensions- in 'geometry'.",
                    "---------------------------------------------",
                    "time (STRING):",
                    "can be empty, a number (as STRING), or a valid",
                    "HDF5 path if the HDF5 file stores a time value.",
                    "Will be written as VTK file title (2nd line).",
                    "If empty, default header will be: 't='.",
                    "---------------------------------------------",
                ],
                "dim": 0,
                "time": "",
            },
            "paths": {
                "_comment": [
                    "---------------------------------------------",
                    "Here, enter the absolute group paths in the input",
                    "HDF5 / DREAM3D file of the respective Datasets.",
                    "---------------------------------------------",
                ],
                "geometry": {
                    "dimensions": "/",
                    "origin": "/",
                    "spacing": "/"
                },
                "cellFeatureData": {
                    "eulerAngles": "/",
                    "phases": "/"
                },
                "cellData": {
                    "_comment": [
                        "---------------------------------------------",
                        "For each cellData, enter HDF5 group path, ",
                        "VTK Dataset Attribute type, VTK dataName,",
                        "VTK dataType, and, optionally, a tag for a",
                        "supplied MICRESS driving file template.",
                        "---------------------------------------------",
                        "Accepted VTK Dataset Attribute types:",
                        "SCALARS, VECTORS, NORMALS, TENSORS, FIELD.",
                        "In the output, this is also the sorting order.",
                        "If FIELD(s) are present, the key 'fieldArrays'",
                        "must hold a string 'arrayName numComponents' for each",
                        "FIELD in consecutive manner with type arrayname (STRING)",
                        "without whitespace, and type numComponents (INTEGER).",
                        "See example below.",
                        "---------------------------------------------",
                        "Accepted VTK dataTypes: ",
                        "bit, unsigned_char, char, unsigned_short, short, ",
                        "unsigned_int, int, unsigned_long, long, float, or double.",
                        "These will only be used as labels in the",
                        "ASCII VTK output. Internal reader from HDF5 uses",
                        "Numpy data types instead, using internal",
                        "VTK -> Numpy type mapping scheme.",
                        "---------------------------------------------",
                        "Tagging: ",
                        "If one or more tags are defined, each must adhere to",
                        "the format '<mytagname>' (without encasing quotes in ",
                        "the driving file, naturally). Each tag's list position",
                        "must comply to it's respective path's list position.",
                        "---------------------------------------------",
                        "Example:",
                        "'paths':                 ['/a', '/b', '/c', '/d', '/e', '/f'],",
                        "'dataNames':             ['aa', 'f1', 'korn', 'f1', 'ee', 'f2'],",
                        "'dataTypes':             ['bit', 'float', 'int', 'int', 'unsigned_char', 'float']",
                        "'datasetAttributeTypes': ['SCALARS', 'FIELD', 'SCALARS', 'FIELD', 'VECTORS', 'FIELD']",
                        "'fieldArrays':           ['arr1OfField1 3', 'arr2OfField1 3', 'arr1OfField2 3']",
                        "'tags':                  ['', '', '<init-grain-structure>', '<field1arr2>']",
                        "",
                        "In the VTK output file, the Dataset Attributes sorting order will be:",
                        "aa, korn, ee, f1 arr1OfField1 arr2OFField1, f2 arr1OfField2.",
                        "In the Driving file output, the following replacements will have ocurred:",
                        "<init-grain-structure> --> myfile.vtk korn",
                        "<field1arr2>           --> myfile.vtk f1 arr2OfField1",
                        "(provided the vtk output file name is 'myfile.vtk').",
                        "---------------------------------------------",
                    ],
                    "paths": [
                        "/",
                    ],
                    "dataNames": [
                        "unnamed",
                    ],
                    "dataTypes": [
                        "unknown",
                    ],
                    "datasetAttributeTypes": [
                        "UNKNOWN",
                    ],
                    "fieldArrays": [
                        "unnamed 0",
                    ],
                    "tags": [
                        ""
                    ]
                }
            }
        },
        "settings": {
            "_comment": [
                "---------------------------------------------",
                "If 'verbose':true settings will be printed",
                "out during conversion.",
                "---------------------------------------------",
            ],
            "input": {
                "dri_template": {
                    "_comment": [
                        "---------------------------------------------",
                        "No settings available for now.",
                        "---------------------------------------------",
                    ]
                },
                "hdf5": {
                    "_comment": [
                        "---------------------------------------------",
                        "cellFeatureDataClipFirstLine:",
                        "Format: (BOOL)",
                        "Will clip off first line of all non-list-like (1D)",
                        "cellFeatureData.",
                        "When to use: e.g. input from DREAM3D where all first",
                        "lines contain zero values.",
                        "---------------------------------------------",
                        "rotate:",
                        "Format: (BOOL)",
                        "If true, will rotate data arrays to comply with the",
                        "MICRESS coordinate system (xyz --> xzy, rotate vector-",
                        "valued cellFeatureData.)",
                        "When to use: e.g. input from DREAM3D.",
                        "---------------------------------------------",
                        "rotateCellDataValues:",
                        "Format: list of (INT) or (STRING).",
                        "If 'data' > 'paths' > 'cellData' contains vector-valued",
                        "data whose values have to be rotated individually, ",
                        "insert their index (start: 0) or 'dataName' here.",
                        "When to use: e.g. for cellData 'EulerAngles'.",
                        "If none present, leave empty list: [].",
                        "---------------------------------------------",
                    ],
                    "cellFeatureDataClipFirstLine": False,
                    "rotate": False,
                    "rotateCellDataValues": [],
                }
            },
            "output": {
                "dri": {
                    "_comment": [
                        "---------------------------------------------",
                        "'makeFilePathsAbsolute':",
                        "Format: (JSON BOOLEAN).",
                        "If true, output file paths that have",
                        "been specified as relative paths and that are inserted",
                        "into a MICRESS driving template file via tagging get",
                        "converted to absolute paths.",
                        "---------------------------------------------",
                    ],
                    "makeFilePathsAbsolute": False
                },
                "txt": {
                    "_comment": [
                        "---------------------------------------------",
                        "No settings available for now.",
                        "---------------------------------------------",
                    ]
                },
                "vtk": {
                    "_comment": [
                        "---------------------------------------------",
                        "These keys specify the output VTK ASCII file format",
                        "- version:      (FLOAT) VTK version in the file header. Default: 2.0.",
                        "- columns:      (INTEGER) Number of columns per line for writing the",
                        "                cellData to ASCII VTK Dataset Attributes. Default: 9.",
                        "---------------------------------------------",
                    ],
                    "version": 2.0,
                    "cellDataColumns": 9
                }
            },
            "verbose": True
        }
    }

    def _init_arg(self, expected_type, value):
        """
        Helper method for constructor.

        Parameters
        ----------
        expected_type: type
            type according to dynamic (derived) class _fields[] attribute
        value: str
            string value from JSON

        Returns
        ------
        type:
            value converted to expected_type

        Raises
        ------
        TypeError
            If type in deserialized JSON file (dict) does not match type in typed class ArgMap.
        """
        if isinstance(value, expected_type):
            return value
        else:
            try:
                return expected_type(**value)
            except TypeError:
                s_value = ''
                if type(value) is not dict:
                    s_value = ' ' + str(value)
                    print('ERROR: value{} has {}, expected {}.'.format(s_value, type(value), expected_type))
                raise TypeError

    def __init__(self, **kwargs):
        field_names, field_types = zip(*self._fields)
        assert ([isinstance(name, str) for name in field_names])
        assert ([isinstance(type_, type) for type_ in field_types])

        for name, field_type in self._fields:
            setattr(self, name, self._init_arg(field_type, kwargs.pop(name)))

        # Check for any remaining unknown arguments
        if kwargs:
            raise TypeError('Invalid arguments(s): {} in {}.'
                            .format(','.join(kwargs), type(self)))

    def pprint(self):
        """
        Prints all non-ArgMapper attribute-value-pairs recursively.
        For printing ArgMap that hold 'settings' to console
        during conversion.
        """
        attr_dict = vars(self)

        # remove unwanted kv pairs
        if "JSON_TEMPLATE" in attr_dict:
            attr_dict.pop("JSON_TEMPLATE")
        for k in attr_dict.keys():
            if k.startswith("_"):
                del attr_dict[k]

        # get items (list of tuples key (str): value (obj))
        attrs_list = vars(self).items()

        # for all other items, print
        attrs_list_other = [tup for tup in attrs_list if not isinstance(tup[1], ArgMapper)]
        if attrs_list_other:
            attrs_list_other.sort()
            print("\n ".join("\t\t%s: %s" % item for item in attrs_list_other))

        # for ArgMap items, call pprint recursively
        attrs_list_argMaps = [tup for tup in attrs_list if isinstance(tup[1], ArgMapper)]
        for argMap in attrs_list_argMaps:
            argMap[1].pprint()


class ArgMap_settingsOutputVtk(ArgMapper):
    r"""
    Subclass for typed deserialization of JSON conversion parameters file.

    See Also
    --------
    ArgMapper : derived class
    ArgMap : deserialization base class
    """
    _fields = [(ArgMapper._COMMENT, list),
               ('version', float),
               ('cellDataColumns', int), ]

    def pprint(self):
        print("\twith output VTK settings:")
        super(ArgMap_settingsOutputVtk, self).pprint()


class ArgMap_settingsOutputTxt(ArgMapper):
    r"""
    Subclass for typed deserialization of JSON conversion parameters file.

    See Also
    --------
    ArgMapper : derived class
    ArgMap : deserialization base class
    """
    _fields = [(ArgMapper._COMMENT, list)]


class ArgMap_settingsOutputDri(ArgMapper):
    r"""
    Subclass for typed deserialization of JSON conversion parameters file.

    See Also
    --------
    ArgMapper : derived class
    ArgMap : deserialization base class
    """
    _fields = [(ArgMapper._COMMENT, list),
               ('makeFilePathsAbsolute', bool)]

    def pprint(self):
        print("\twith output Dri settings:")
        super(ArgMap_settingsOutputDri, self).pprint()


class ArgMap_settingsOutput(ArgMapper):
    r"""
    Subclass for typed deserialization of JSON conversion parameters file.

    See Also
    --------
    ArgMapper : derived class
    ArgMap : deserialization base class
    """
    _fields = [('dri', ArgMap_settingsOutputDri),
               ('txt', ArgMap_settingsOutputTxt),
               ('vtk', ArgMap_settingsOutputVtk)]


class ArgMap_settingsInputHdf5(ArgMapper):
    r"""
    Subclass for typed deserialization of JSON conversion parameters file.

    See Also
    --------
    ArgMapper : derived class
    ArgMap : deserialization base class
    """
    _fields = [(ArgMapper._COMMENT, list),
               ('cellFeatureDataClipFirstLine', bool),
               ('rotate', bool),
               ('rotateCellDataValues', list)]

    def pprint(self):
        print("\twith input HDF5 settings:")
        super(ArgMap_settingsInputHdf5, self).pprint()


class ArgMap_settingsInputDri_template(ArgMapper):
    r"""
    Subclass for typed deserialization of JSON conversion parameters file.

    See Also
    --------
    ArgMapper : derived class
    ArgMap : deserialization base class
    """
    _fields = [(ArgMapper._COMMENT, list)]


class ArgMap_settingsInput(ArgMapper):
    r"""
    Subclass for typed deserialization of JSON conversion parameters file.

    See Also
    --------
    ArgMapper : derived class
    ArgMap : deserialization base class
    """
    _fields = [('dri_template', ArgMap_settingsInputDri_template),
               ('hdf5', ArgMap_settingsInputHdf5)]


class ArgMap_settings(ArgMapper):
    r"""
    Subclass for typed deserialization of JSON conversion parameters file.

    See Also
    --------
    ArgMapper : derived class
    ArgMap : deserialization base class
    """
    _fields = [(ArgMapper._COMMENT, list),
               ('input', ArgMap_settingsInput),
               ('output', ArgMap_settingsOutput),
               ('verbose', bool)]

    def pprint(self):
        print("\twith General Settings:")
        super(ArgMap_settings, self).pprint()


class ArgMap_dataDataGeometry(ArgMapper):
    r"""
    Subclass for typed deserialization of JSON conversion parameters file.

    See Also
    --------
    ArgMapper : derived class
    ArgMap : deserialization base class
    """
    _fields = [('dimensions', str),
               ('origin', str),
               ('spacing', str), ]


class ArgMap_dataDataCellFeatureData(ArgMapper):
    r"""
    Subclass for typed deserialization of JSON conversion parameters file.

    See Also
    --------
    ArgMapper : derived class
    ArgMap : deserialization base class
    """
    _fields = [('eulerAngles', str),
               ('phases', str), ]


class ArgMap_dataPathsCellData(ArgMapper):
    r"""
    Subclass for typed deserialization of JSON conversion parameters file.

    See Also
    --------
    ArgMapper : derived class
    ArgMap : deserialization base class
    """
    _fields = [(ArgMapper._COMMENT, list),
               ('paths', list),
               ('dataNames', list),
               ('dataTypes', list),
               ('datasetAttributeTypes', list),
               ('fieldArrays', list),
               ('tags', list), ]


class ArgMap_dataPaths(ArgMapper):
    r"""
    Subclass for typed deserialization of JSON conversion parameters file.

    See Also
    --------
    ArgMapper : derived class
    ArgMap : deserialization base class
    """
    _fields = [(ArgMapper._COMMENT, list),
               ('geometry', ArgMap_dataDataGeometry),
               ('cellFeatureData', ArgMap_dataDataCellFeatureData),
               ('cellData', ArgMap_dataPathsCellData), ]


class ArgMap_dataOther(ArgMapper):
    r"""
    Subclass for typed deserialization of JSON conversion parameters file.

    See Also
    --------
    ArgMapper : derived class
    ArgMap : deserialization base class
    """
    _fields = [(ArgMapper._COMMENT, list),
               ('dim', int),
               ('time', str), ]


class ArgMap_dataFilesOutput(ArgMapper):
    r"""
    Subclass for typed deserialization of JSON conversion parameters file.

    See Also
    --------
    ArgMapper : derived class
    ArgMap : deserialization base class
    """
    _fields = [('dri', str),
               ('txt', str),
               ('vtk', str), ]


class ArgMap_dataFilesInput(ArgMapper):
    r"""
    Subclass for typed deserialization of JSON conversion parameters file.

    See Also
    --------
    ArgMapper : derived class
    ArgMap : deserialization base class
    """
    _fields = [('hdf5', str),
               ('dri_template', str), ]


class ArgMap_dataFiles(ArgMapper):
    r"""
    Subclass for typed deserialization of JSON conversion parameters file.

    See Also
    --------
    ArgMapper : derived class
    ArgMap : deserialization base class
    """
    _fields = [(ArgMapper._COMMENT, list),
               ('input', ArgMap_dataFilesInput),
               ('output', ArgMap_dataFilesOutput), ]


class ArgMap_data(ArgMapper):
    r"""
    Subclass for typed deserialization of JSON conversion parameters file.

    See Also
    --------
    ArgMapper : derived class
    ArgMap : deserialization base class
    """
    _fields = [('files', ArgMap_dataFiles),
               ('other', ArgMap_dataOther),
               ('paths', ArgMap_dataPaths), ]


class ArgMap(ArgMapper):
    r"""
    Base class for typed deserialization of JSON conversion parameters file.

    Note
    ----
    Must match master template for JSON conversion file for serialization in this module.

    See Also
    --------
    ArgMapper : derived class
    """
    _fields = [(ArgMapper._COMMENT, list),
               ('data', ArgMap_data),
               ('settings', ArgMap_settings), ]
