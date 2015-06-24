#!/usr/bin/env python

from distutils.core import setup

# Get version number from package
exec(open('phyloprofilerlib/version.py').read())

setup(
    name='PhyloProfiler',
    version=__version__,
    description='A short wrappper for finding presence/absence/abundance of pathways from metagenomic data.',
    author='Ashwini Patil',
    author_email='patil.ashwini1091@gmail.com',
    url='https://github.com/PennChopMicrobiomeProgram',
    packages=['phyloprofilerlib'],
    scripts=['scripts/phyloprofiler.py'],
    )
