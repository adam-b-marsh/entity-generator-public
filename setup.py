#!/usr/bin/env python3
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="abc-crm-entity-generator",
    use_scm_version=True,
    author="NSS",
    description="CRM Entity Generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="/crm-entity-generator",
    license="Proprietary",
    packages=["crm_entity_generator"],
    platforms=["any"],
    zip_safe=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    setup_requires=["setuptools>=42", "wheel", "setuptools_scm"],
    install_requires=[
        "abc-protobufs",
        "grpcio",
    ],
    tests_require=[
        "pytest",
        "pytest-cov",
        "pytest-helpers-namespace",
    ],
)
