__author__ = 'johan'

from setuptools import setup

setup(
    name="torganizer",
    version="0.0.1",
    author="Johan Lyheden",
    author_email="torganizer-johan@lyheden.com",
    description="Python module to extract, move, rename files into proper locations",
    license="BSD",
    packages=['torganizer', 'tests'],
    test_suite="tests",
    install_requires=['mutagen', 'pyyaml'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License"
    ]
)