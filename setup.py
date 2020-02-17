#!/usr/bin/env python
# Author:  gortiz-v
# Purpose: setup
# Created: 2018-10-22
#
# The MIT License (MIT)

# Copyright (c) 2018 Gerardo Ortiz

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as fp:
    long_description = fp.read()

setup(
    name='bamboopy',
    version='0.0.7',
    url='https://github.com/gortiz-v/bamboopy',
    license='MIT',
    author='Gerardo Ortiz',
    author_email='gortiz@netquest.com',
    description="A python wrapper around BambooHR's APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    platforms='OS Independent',
    packages=['bamboopy'],
    include_package_data=True,
    install_requires=['rfc6266', 'xmltodict'],
    keywords=['Bamboo', 'HR', 'BambooHR', 'API'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)