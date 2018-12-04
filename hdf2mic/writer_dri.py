# -*- coding: utf-8 -*-
r"""

This module contains the MICRESS input driving file writer for the script hdf2mic.py.
"""
import os
import re
from hdf2mic.data import *
from hdf2mic.writer import *
from hdf2mic.arg_mapping import ArgMap_settingsOutputDri


class DriWriter(Writer):
    """

    Reads a tagged MICRESS driving template file, replaces tags and writes result.
    Tags in the template are of the form <mytagname>.

    Notes
    -----
    Use with a context manager (see example).

    Examples
    --------
    Write to file.

    >>> #...
    >>> data = reader.data
    >>> writer = DriWriter(ouputfile_txt)
    >>> with writer as f:
    ...     writer.write(data)
    """

    def __init__(self, filepath):
        Writer.__init__(self, filepath)
        self.template = None
        self._msg_warn_tag = "Warning: dri template is missing tag: {}."
        self._msg_err_outfile = "Error: driving template file requires output file {}, but was not found. Abort."
        self._inputfile_template = None

    def _replace(self, tag, replacement):
        match = re.match('(<.*>)', tag)
        if not match or len(match.groups()) != 1:
            if not tag:
                print("Warning: tag not specified for:\n\treplacement = {}\n\tin template = {}."
                    .format(replacement, self._inputfile_template))
            else:
                print("Warning: tag '{}' does not comply with recommended format '<mytagname>' for "
                      "\n\treplacement = {}".format(tag, replacement))
        if tag in self.template:
            self.template = self.template.replace(tag, str(replacement))
        else:
            print(self._msg_warn_tag.format(tag))

    def write(self, data, settings, verbose, inputfile_template, f_vtk='', f_txt=''):
        """

        Parameters
        ----------
        data : Data
            hdf2mic Data object
        settings : ArgMap_settingsOutputDri
        verbose : bool
        inputfile_template : str
            the hdf2mic input MICRESS driving template file
        f_vtk : str
            the optional hdf2mic output vtk file
        f_txt : str
            the optional hdf2mic output txt file (grain properties)

        Raises
        ------
        AttributeError
             If not called inside a context manager.
        """
        super(DriWriter, self).write(data, settings, verbose)
        self._inputfile_template = inputfile_template

        # check output files existence
        # os.path.isfile(filename_txt)
        # os.path.isfile(filename_vtk)

        # read driving template file
        template = ""
        try:
            with open(inputfile_template, 'r') as f_t:
                template = f_t.read()

            if not template:
                raise Hdf2Mic_DrivingFileTaggingError(
                    "Dri_writer: processing driving template file was implied, "
                    "but template file {} was empty."
                        .format(inputfile_template)
                )
            else:
                self.template = template

                # replace implicit tags:
                # regarding TAG_CELLS: DRI requires #cells, not #nodes,
                # so decrement by one.
                for i in range(data.dim):
                    self._replace(Data.DRI_TAG_CELLS[i],
                                  str(data.dimensions[i] - 1))

                self._replace(Data.DRI_TAG_SPACING,
                              data.spacing[0])

                # DEVNOTE: tag distinct-phases deactivated in v0.5
                # as per request by RA
                # self._replace(Data.INPUT_DRI_TAG_PHASES,
                #               len(np.unique(data.phases)))

                if f_txt:
                    if (os.path.isfile(f_txt)):
                        if self.settings.makePathsAbsolute:
                            f_txt = os.path.abspath(f_txt)
                        self._replace(Data.DRI_TAG_GRAIN_PROPERTIES, f_txt)
                    else:
                        raise Hdf2Mic_DrivingFileTaggingError(
                            self._msg_err_outfile.format(f_txt))

                # replace user-defined tags
                if f_vtk:
                    if (os.path.isfile(f_vtk)):
                        for tupl in data.celldata:
                            # from Data.celldata:
                            # tuples have either length 5 or 7
                            dataName = tupl[1]
                            tag = tupl[-1]

                            # replacement:
                            fieldArrayName = ""
                            if (len(tupl) == 7):
                                fieldArrayName = tupl[-2]

                            if self.settings.makePathsAbsolute:
                                f_vtk = os.path.abspath(f_vtk)

                            replacement = f_vtk + " " + dataName
                            if fieldArrayName:
                                replacement += " " + fieldArrayName

                            self._replace(tag, replacement)
                    else:
                        raise Hdf2Mic_DrivingFileTaggingError(
                            self._msg_err_outfile.format(f_vtk))

                # save formatted driving template file
                self._f.write(self.template)

        except IOError as e:
            print("ERROR: could not find or open input file \'{}\'.".format(inputfile_template))
