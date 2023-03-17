########################################################
# This program builds .so files from .py files
# and delete '.py', '.c' and '.pyc' files.# install cpython:
# sudo pip install cython
# Command to run build:
# python compile.py build_ext --inplace
########################################################

import os
import sys
from distutils.core import setup
from distutils.extension import Extension
from pathlib import Path
from Cython.Build import cythonize

# Get current folder path
mash_path = os.path.dirname(sys.argv[0])

# Get .py files
extensions = []
exclude_files = ['compile', '__init__', 'main', 'gunicorn_conf']


def build(exclude_directories):
    """build .so files from .py files"""
    for file in list(Path(mash_path).glob('**/*.py')):
        # Take out file name without .py ext
        filename = Path(file).resolve().stem
        if file.stat().st_size != 0 and filename not in exclude_files:
            rel_path = os.path.relpath(os.path.dirname(file.absolute().as_posix()), mash_path)
            for directory in exclude_directories:
                if rel_path.startswith(directory):
                    continue
            package_name = rel_path.replace('/', '.') + '.' + filename if rel_path != '.' else filename
            extensions.append([Extension(package_name, [str(file)])])

    for ext in extensions:
        setup(ext_modules=cythonize(ext, compiler_directives={
            'c_string_type': 'str',
            'c_string_encoding': 'utf8',
            'language_level': 3}))


def delete_files(file_type, exclude_directories):
    c_files = list(Path(mash_path).glob('**/*.' + file_type))
    for c_file in c_files:
        filename = Path(c_file).resolve().stem
        rel_path = os.path.relpath(os.path.dirname(c_file.absolute().as_posix()), mash_path)
        for directory in exclude_directories:
            if rel_path.startswith(directory):
                continue
        if filename not in exclude_files:
            c_file.unlink()


# As pydantic(used by fastapi) will raise error when compile with cython, so we exclude the api codes and schema codes
build(exclude_directories=['app/api', 'app/schemas'])
delete_files(file_type='py', exclude_directories=['app/api', 'app/schemas'])
delete_files(file_type='c', exclude_directories=['app/api', 'app/schemas'])
delete_files(file_type='pyc', exclude_directories=['app/api', 'app/schemas'])
