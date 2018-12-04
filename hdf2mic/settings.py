# -*- coding: utf-8 -*-
r"""

This module contains the IO settings classes for the script hdf2mic.py.
"""
from hdf2mic.arg_mapping import ArgMap_settingsInputHdf5, ArgMap_settingsOutput, ArgMap_settingsOutputDri, \
    ArgMap_settingsOutputVtk, ArgMap_settingsOutputTxt
from hdf2mic.exceptions import Hdf2Mic_InitArgError
#from deprecated import deprecated


class Settings(object):
    def __init__(self):
        pass

    def pprint(self):
        """
        Prints the settings.
        """
        attrs_list = vars(self).items()
        attrs_list.sort()
        print("\n ".join("\t%s: %s" % item for item in attrs_list))

#@deprecated(reason="v0.4 --> v0.5: settings/input/hdf5 changed from application-specific"
#                   " (implicit settings) to case-specific (all settings explicit). So now"
#                   "Reader can use ArgMap_settingsInputHdf5 directly.")
class ReaderSettings(Settings):

    def __init__(self, settings, verbose):
        Settings.__init__(self)

        self.rotate = None
        self.cellFeatureDataClipFirstLine = None
        self.cellFeatureDataPath = None
        self.cellDataToRotate = None

        assert isinstance(settings, ArgMap_settingsInputHdf5)
        self.application = settings.application
        appSettings = None

        if (self.application == "DREAM3D"):
            appSettings = settings.applicationSettings.DREAM3D

            self.rotate = True
            self.cellFeatureDataClipFirstLine = True
            self.cellFeatureDataPath = appSettings.cellFeatureDataPath
            self.cellDataToRotate = appSettings.cellDataToRotate

        elif (self.application == "MICRESS"):
            appSettings = settings.applicationSettings.MICRESS

            self.rotate = False
            self.cellFeatureDataClipFirstLine = False

        else:
            raise Hdf2Mic_InitArgError("Reader: unknown settings > input > hdf5 > application:"
                                       "{}. Supported: DREAM3D, MICRESS".format(self.application))

        if verbose:
            self.pprint()

    def pprint(self):
        print("\twith input HDF5 settings:")
        super(ReaderSettings, self).pprint()


class DriWriterSettings(Settings):

    def __init__(self, settings, verbose):
        Settings.__init__(self)

        self.makePathsAbsolute = None

        assert isinstance(settings, ArgMap_settingsOutputDri)

        self.makePathsAbsolute = settings.makeFilePathsAbsolute

        if verbose:
            self.pprint()

    def pprint(self):
        print("\twith output writer DRI settings:")
        super(DriWriterSettings, self).pprint()


class VtkWriterSettings(Settings):

    def __init__(self, settings, verbose):
        Settings.__init__(self)

        self.version = None
        self.columns = None

        assert isinstance(settings, ArgMap_settingsOutputVtk)

        self.version = settings.version
        self.columns = settings.cellDataColumns

        if verbose:
            self.pprint()

    def pprint(self):
        print("\twith output writer VTK settings:")
        super(VtkWriterSettings, self).pprint()


class TxtWriterSettings(Settings):

    def __init__(self, settings, verbose):
        Settings.__init__(self)

        assert isinstance(settings, ArgMap_settingsOutputTxt)

        if verbose:
            self.pprint()

    def pprint(self):
        print("\twith output writer TXT settings:")
        super(TxtWriterSettings, self).pprint()
