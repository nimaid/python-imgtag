import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="imgtag",
    version="0.1.0",
    author="Ella Jameson",
    author_email="ellagjamson@gmail.com",
    description="Simple XMP Image Tag & Metadata Editing Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nimaid/python-imgtag",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)