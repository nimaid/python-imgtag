# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='imgtag',
    version='0.1.0',
    description='Simple XMP Image Tag & Metadata Editing Library',
    long_description=readme,
    author='Ella Jameson (nimaid)',
    author_email='ellagjameson@gmail.com',
    url='https://github.com/nimaid/python-imgtag',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

