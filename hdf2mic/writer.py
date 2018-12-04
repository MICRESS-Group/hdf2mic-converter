# -*- coding: utf-8 -*-
r"""

This module contains the file writer base class for the script hdf2mic.py.
"""
from hdf2mic.arg_mapping import ArgMap_settingsOutput, ArgMap_settingsOutputDri, ArgMap_settingsOutputVtk, \
    ArgMap_settingsOutputTxt
from hdf2mic.exceptions import *
from hdf2mic.data import *
from hdf2mic.settings import DriWriterSettings, VtkWriterSettings, TxtWriterSettings


class Writer(object):
    """

    Base class for file writers.

    Notes
    -----
    Use with a context manager (see example).

    Examples
    --------
    Write to file.

    >>> #...
    >>> data = reader.data
    >>> writer = Writer(ouputfile)
    >>> with writer as f:
    ...     writer.write(data)
    """

    def __init__(self, filepath):
        self._f_path = filepath
        self.settings = None

        self._EXCEPTIONS_INITARG = """Tried to init writer attributes outside a with-statement.
            Instead, init writer attributes inside a with statement like this:
            writer = Writer(fp)
            with writer as file:
            \t#initialize writer arguments..."""

    def __enter__(self):
        # trysetattr etc goes here
        # self._f = open(self._f_path, 'r')
        self._f = open(self._f_path, 'w')
        return self._f

    def __exit__(self, type, value, traceback):
        # exception handling goes here
        self._f.close()

    def write(self, data, settings, verbose):
        """

        Parameters
        ----------
        data : Data
            hdf2mic Data object
        settings : ArgMap_settingsOutput
            hdf2mic settings output
        verbose : bool
            Print operations

        Raises
        ------
        AttributeError
             If not called inside a context manager.
        """
        assert isinstance(data, Data)
        assert isinstance(verbose, bool)

        if isinstance(settings, ArgMap_settingsOutputDri):
            self.settings = DriWriterSettings(settings, verbose)
        elif isinstance(settings, ArgMap_settingsOutputVtk):
            self.settings = VtkWriterSettings(settings, verbose)
        elif isinstance(settings, ArgMap_settingsOutputTxt):
            self.settings = TxtWriterSettings(settings, verbose)
        else:
            self.settings = None
