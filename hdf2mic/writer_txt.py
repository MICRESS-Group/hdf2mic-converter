# -*- coding: utf-8 -*-
r"""

This module contains the MICRESS input TXT file writer for the script hdf2mic.py.
"""

from hdf2mic.exceptions import *
from hdf2mic.writer import *
from hdf2mic.arg_mapping import ArgMap_settingsOutputTxt


class TxtWriter(Writer):
    """

    Writes Numpy Arrays of EulerAngles and Phases to MICRESS input TXT.

    Notes
    -----
    Use with a context manager (see example).

    Examples
    --------
    Write to file.

    >>> #...
    >>> data = reader.data
    >>> writer = TxtWriter(ouputfile_txt)
    >>> with writer as f:
    ...     writer.write(data)
    """

    def write(self, data, settings, verbose):
        """

        Parameters
        ----------
        data : Data
            hdf2mic Data object
        settings : ArgMap_settingsOutputTxt
        verbose : bool

        Raises
        ------
        AttributeError
             If not called inside a context manager.
        """
        super(TxtWriter, self).write(data, settings, verbose)

        try:
            for kornID in range(data.grain_count):
                self._f.write("# {}\n".format(kornID + 1))
                if data.phases is not None:
                    self._f.write("{}\n".format(data.phases[kornID, 0]))
                if data.angles is not None:
                    for columnID in range(data.angles.shape[1]):
                        self._f.write("{}\n".format(data.angles[kornID, columnID]))
        except AttributeError:
            raise Hdf2Mic_InitArgError(self._EXCEPTIONS_INITARG)
