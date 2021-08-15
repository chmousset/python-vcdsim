#!/usr/bin/env python3

import sys
from setuptools import setup
from setuptools import find_packages


if sys.version_info[:3] < (3, 3):
    raise SystemExit("You need Python 3.3+")


requirements = []  # "migen" is an optional requirement

setup(
    name="vcdsim",
    version="0.0.0",
    long_description_content_type='text/markdown',
    description="Using Value Chande Dump files as stimulus for hardware simulation",
    long_description=open("README.md").read(),
    author="Charles-Henri Mousset",
    author_email="ch.mousset@gmail.com",
    download_url="https://github.com/chmousset/python-vcdsim",
    packages=find_packages(),
    install_requires=requirements,
    test_suite="vcdsim.test",
    license="BSD",
    platforms=["Any"],
    keywords=["HDL", "ASIC", "FPGA", "hardware design"],
    classifiers=[
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "Environment :: Console",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
    ],
    entry_points={
        'console_scripts': ['vcdconvert=vcdsim.convert:main'],
    },
)
