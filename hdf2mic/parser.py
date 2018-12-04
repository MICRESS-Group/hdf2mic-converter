# -*- coding: utf-8 -*-
r"""

This module contains classes that handle the command-line input of the script hdf2mic.py.
"""

import argparse
import json
from arg_mapping import *


class Parser(object):
    """Parser description

    Serves script hdf2mic.py as frontend and converts user-defined arguments into a usable form for other modules.
    Constructor sets up argparse parsers.

    Attributes
    ----------
    args_script : argparse.Namespace
        command-line input arguments
    args_conversion: ArgMap
        deserialized conversion parameters from JSON file
    """

    PARSER_ERR_MSG_PROBABLE_REASONS = """
    \tProbable causes for this:
    \t- You were reusing a JSON template of another hdf2mic version (possibly incompatible). Generate a new one.
    \t- You changed the JSON structure (for example removed one argument instead of leaving it empty.)
    \t- You entered something which is not valid JSON syntax (check with a JSON Linter online)."""

    def __init__(self):
        self._parser = argparse.ArgumentParser(
            description='Convert DREAM3D HDF5 synthetic microstructure file'
                        'to MICRESS input files TXT and ASCII VTK'
        )
        self._subparsers = self._parser.add_subparsers(help='commands', dest='command')

        # convert command
        self._subparser_convert = self._subparsers.add_parser('convert',
                                                              help='Convert DREAM3D/HDF5 to MICRESS input.')
        self._subparser_convert.add_argument('filepath',
                                             action='store',
                                             help='The JSON file holding the conversion parameters.'
                                                  'Generate template with command \'template\'.')

        # template command
        self._subparser_template = self._subparsers.add_parser('template',
                                                               help='Generate template JSON conversion parameters file.')
        self._subparser_template.add_argument('filepath',
                                              action='store',
                                              help='Filepath / Filename location where the script shall generate the template JSON conversion file.')

        self.args_script = None

    def byteify(self, string_container):
        r"""Converts contained unicode strings to normal strings.

        The json package's function json.loads to deserialize a JSON file into a dict returns a dict with unicode
        strings. To deserialize the JSON into a typed object, it is passed to the ArgMap constructor which only
        can deal with normal string dicts and fails with unicode string dicts. This method solves that problem.



        Parameters
        ----------
        string_container: {dict, list, str}
            Containing possibly unicode strings

        Returns
        -------
        string_container: {dict, list, str}
            Containing only normal strings

        Note
        ----
        This method is memory-hungry. For large dicts (~ 500 levels), should be replaced by more efficient
        method, see reference [1].

        References
        ----------
        .. [1] Mark Amery, "How to get string objects instead of Unicode from JSON?",
           URL: https://stackoverflow.com/a/13105359/8116031. For more efficient methods,
           see the answers by Mirec Miskuf and Brutus in the same thread.
        """
        if isinstance(string_container, dict):
            return {self.byteify(key): self.byteify(value)
                    for key, value in string_container.iteritems()}
        elif isinstance(string_container, list):
            return [self.byteify(element) for element in string_container]
        elif isinstance(string_container, unicode):
            return string_container.encode('utf-8')
        else:
            return string_container

    def parse(self):
        r"""Parses command line input arguments

        Returns
        -------
        [ArgMap]
            None if input argument was 'template', deserialized conversion parameters if input argument was 'convert'.

        Raises
        ------
        TypeError
            If internal JSON template dict and typed version (ArgMap) do not match.
        """
        # parse command line input arguments
        self.args_script = self._parser.parse_args()
        filepath = self.args_script.filepath

        # Before using JSON: self-check if JSON template
        # mapping classes match corresponding template dictionary:
        try:
            print('Self-checking internal JSON mapping...')
            check_mapping = ArgMap(**ArgMapper.JSON_TEMPLATE)
            print('Self-checking internal JSON mapping succeeded.')
        except TypeError as err:
            print('ERROR: Self-check of internal data structure for the conversion parameters JSON file failed.\n'
                  '       Contact developer, or compare internal JSON template dictionary to it\'s corresponding\n'
                  '       internal mapping class \'ArgMap\'. Probably someone has changed one of both and forgot\n'
                  '       to update the other.')
            raise err

        # Everything okay, examine script input args:
        if self.args_script.command == 'template':

            print('Saving template JSON conversion parameters file as {}.'.format(filepath))

            with open(filepath, 'w') as outfile:
                template_str = json.dump(ArgMapper.JSON_TEMPLATE,
                                         outfile, indent=4, sort_keys=True,
                                         separators=(',', ': '))
            return None

        elif self.args_script.command == 'convert':

            print('Parsing conversion parameters in {}...'.format(filepath))
            template_dict = None
            with open(filepath, 'r') as json_data:
                try:
                    template_dict = json.load(json_data)
                    # convert returned unicode dict to str dict
                    template_dict = self.byteify(template_dict)
                except ValueError as error:
                    print("ERROR: Failed to parse {} as JSON: incorrect syntax. {}"
                        .format(filepath, self.PARSER_ERR_MSG_PROBABLE_REASONS))
                    raise error

            if template_dict is not None and type(template_dict) is dict:

                try:
                    self.args_conversion = ArgMap(**template_dict)
                    return self.args_conversion
                except TypeError as error:
                    print("ERROR: Failed to parse '{}' as JSON: ecountered unexpected type. {}"
                        .format(filepath, self.PARSER_ERR_MSG_PROBABLE_REASONS))
                    raise error
