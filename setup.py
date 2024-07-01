# setup.py

from setuptools import setup, find_packages

setup(
    name="tigerbeetle_client",
    version="0.1.0",
    description="Python client for TigerBeetle",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="Aditya Agarwal",
    author_email="aditya@spendthebits.com",
    url="https://github.com/SpendTheBits/tigerbeetle-client-python",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
