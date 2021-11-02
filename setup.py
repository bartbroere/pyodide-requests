import os
from setuptools import setup, find_packages

setup(
    name="requests",
    version="2021.11.2",
    description="Requests, polyfilled for Pyodide",
    long_description="# Requests, polyfilled for Pyodide",
    long_description_content_type="text/markdown",
    url="https://github.com/bartbroere/pyodide-requests",
    author="Bart Broere",
    author_email="mail@bartbroere.eu",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
    ],
)
