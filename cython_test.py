import cython
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("texture_dilate.pyx")
)