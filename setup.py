#!/usr/bin/python3
#run the code below to get the needed executable for the pathfind external
#python3 ./setup.py build_ext --inplace
#you can delete pathfind.c and build/ after the compilation
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("pathfind.pyx"),
    zip_safe=False,
)
