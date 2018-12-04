# -*- coding: utf-8 -*-
r"""

For installing the hdf2mic package with setuptools to a Python env.

Notes
-----
Unsure if installation fails when the script hdf2mic.py is on the same dir level as the folder hdf2mic.
This is necessary so that hdf2mic.py finds the import modules there when called directly withou installation.

If the script shall be used via installation and it fails, try moving the script to bin/ and adjust the scripts
entry in the setup below.

TODO
----
Test installation. Script was only tested by calling it directly so far.
"""


from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='hdf2mic',
      version='0.5',
      description='Convert DREAM3D HDF5 synthetic microstructure file'
                  'to MICRESS input files TXT and ASCII VTK',
      long_description=readme(),
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'License :: Free for non-commercial use',
          'Programming Language :: Python :: 2.7',
          'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
      ],
      url='https://git.rwth-aachen.de/groups/icmeaix',
      author='Johannes Wasmer',
      author_email='j.wasmer@access-technology.de',
      license='',
      packages=['hdf2mic'],
      install_requires=[
          'numpy',
          'h5py',
          'Deprecated'#, json???
      ],
      scripts=['hdf2mic'], #or scripts=['bin/hdf2mic']???
      zip_safe=False)