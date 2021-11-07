from setuptools import setup, find_packages

setup(
    name="requests",
    version="2021.11.7",
    description="Requests, for Pyodide",
    long_description="# Requests, for Pyodide",
    long_description_content_type="text/markdown",
    url="https://github.com/bartbroere/pyodide-requests",
    author="Bart Broere",
    author_email="mail@bartbroere.eu",
    packages=['requests'],
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
    ],
)
