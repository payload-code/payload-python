import os
import sys
try:
    from io import open
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

pkg_name = 'payload'

directory = os.path.abspath(os.path.dirname(__file__))

sys.path.insert(0, os.path.join(directory, pkg_name))

from version import __version__

with open(os.path.join(directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='payload-api',
    version='.'.join(map(str,__version__)),
    description='Payload Python Library',
    author='Payload',
    author_email='help@payload.co',
    url='https://github.com/payload-code/payload-python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=['requests', 'six'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
