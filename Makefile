PYTHON_BIN = python
CONDA_ENV = imgtag

SHELL = /bin/bash

ACTIVATE_CONDA = source $$(conda info --base)/etc/profile.d/conda.sh && conda activate &&
ACTIVATE_ENV = ${ACTIVATE_CONDA} conda activate ${CONDA_ENV} &&

PYPI_TOKEN_FILE = pypi.token
PYPI_TOKEN = $$(cat ${PYPI_TOKEN_FILE})

build:
	${ACTIVATE_ENV} ${PYTHON_BIN} setup.py sdist bdist_wheel
upload:
	${ACTIVATE_ENV} ${PYTHON_BIN} -m twine upload -u __token__ -p ${PYPI_TOKEN} dist/*
clean:
	rm -rf ./build/
	rm -rf ./dist/
	rm -rf ./*.egg-info/
	rm -rf ./**/__pycache__/
prepare:
	${ACTIVATE_ENV} ${PYTHON_BIN} -m pip install --user --upgrade setuptools wheel twine
environment:
	${ACTIVATE_CONDA} conda env create -f environment.yml
run_python:
	${ACTIVATE_ENV} ${PYTHON_BIN}