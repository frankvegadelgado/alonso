from pathlib import Path

import setuptools

VERSION = "0.0.8"

NAME = "alonso"

INSTALL_REQUIRES = [
    "mendive>=0.0.5",
]

setuptools.setup(
    name=NAME,
    version=VERSION,
    description="Compute an Approximate Vertex Cover for undirected graph encoded in DIMACS format.",
    url="https://github.com/frankvegadelgado/alonso",
    project_urls={
        "Source Code": "https://github.com/frankvegadelgado/alonso",
        "Documentation Research": "https://dev.to/frank_vega_987689489099bf/challenging-the-unique-games-conjecture-12mi",
    },
    author="Frank Vega",
    author_email="vega.frank@gmail.com",
    license="MIT License",
    classifiers=[
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
    ],
    python_requires=">=3.10",
    # Requirements
    install_requires=INSTALL_REQUIRES,
    packages=["alonso"],
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    entry_points={
        'console_scripts': [
            'mvc = alonso.app:main',
            'test_mvc = alonso.test:main',
            'batch_mvc = alonso.batch:main'
        ]
    }
)