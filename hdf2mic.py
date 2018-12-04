#!/usr/bin/env python
"""hdf2mic.py script

Converts DREAM3D HDF5 synthetic microstructure file to MICRESS input files TXT and ASCII VTK.

Notes
-----
Calling via 'python hdf2mic.py' requires hdf2mic modules folder in the same folder. Follow printed help instructions.
Alternative: install the whole package to Python env, then call 'hdf2mic' directly. See setup.py.

Developer Notes:
TODO: rotations in reader.py (search for 'if (self.settings.rotate'): check if conditions for rotation are correct
Reason: implemented rotation in mic2hdf, had to extend the conditions a bit so that it worked.
        Meaning: in mic2hdf, the added condition is 'data_numComponents == 3'.
        (example: for 3D angles, numComponents==data.shape[1]==3)
        If false, rotMat.py rotate() is not called.
        Not sure if this should be added in the current hdf2mic implementation, or if it's not necessary.
"""
import os
from hdf2mic.parser import Parser
from hdf2mic.arg_mapping import ArgMap
from hdf2mic.reader import Reader
from hdf2mic.data import Data
from hdf2mic.writer_txt import TxtWriter
from hdf2mic.writer_vtk import VtkWriter
from hdf2mic.writer_dri import DriWriter

# Execution code:
if __name__ == "__main__":
    print('hdf2mic log:')

    # parse input args
    parser = Parser()
    print('Parsing input arguments...')
    args = None
    try:
        args = parser.parse()
    except KeyError as err:
        print("A KeyError occurred when parsing the JSON input. {}"
            .format(parser.PARSER_ERR_MSG_PROBABLE_REASONS))
        raise err

    if args:
        # init reader
        assert isinstance(args, ArgMap)

        fin = args.data.files.input
        fout = args.data.files.output
        sout = args.settings.output
        sverbose = args.settings.verbose

        data = None
        reader = Reader(fin.hdf5)
        writer = None

        # init reader's attributes (hdf2mic script parameters)
        try:
            print('Reading {}...'.format(fin.hdf5))
            with reader as h5file:
                data = reader.read(args, sverbose)
                assert isinstance(data, Data)

            try:
                # write data to TXT file
                if fout.txt and (fout.txt.lower() != '.txt'):
                    writer = TxtWriter(fout.txt)
                    with writer as f:
                        print("Writing TXT: {}".format(f.name))
                        writer.write(data, sout.txt, sverbose)
                else:
                    fout.txt = ""

                # get VTK formatting, write data to VTK file
                if fout.vtk and (fout.vtk.lower() != '.vtk'):
                    writer = VtkWriter(fout.vtk)
                    with writer as f:
                        print("Writing VTK: {}".format(f.name))
                        writer.write(data, sout.vtk, sverbose)
                else:
                    fout.vtk = ""

                # write MICRESS driving file if template has been supplied
                if fin.dri_template and (fin.dri_template.lower() != '.txt') and (fin.dri_template.lower() != '.dri'):
                    if fout.dri and (fout.dri.lower() != '.txt') and (fout.dri.lower() != '.dri'):
                        writer = DriWriter(fout.dri)
                        with writer as f:
                            print("Writing DRI: {}".format(os.path.normpath(f.name)))
                            writer.write(data, sout.dri, sverbose,
                                         fin.dri_template, fout.vtk, fout.txt)

                print("Done.")

            except IOError as e:
                print("ERROR: could not create or open output file \'{}\'.".format(f.name))

        except IOError as e:
            print("ERROR: could not find or open input file \'{}\'.".format(fin.hdf5))
