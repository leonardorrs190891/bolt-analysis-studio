#!/usr/bin/env python
"""
Bolt Analysis Studio v4.0 - Setup Script
Prof. Leonardo Rosa Ribeiro da Silva, PhD | January 2026
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="bolt-analysis-studio",
    version="1.0.0",
    author="Prof. Leonardo Rosa Ribeiro da Silva, PhD; Neilon de Souza da Silva, PhD",
    author_email="leorrs@ancora_interna.br",
    description="Comprehensive bolted joint analysis software for oil and gas applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    package_data={
        "bolt_analysis_studio.core.databases": ["*.json"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Manufacturing",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "matplotlib>=3.5.0",
        "PyQt6>=6.4.0",
    ],
    extras_require={
        "reports": [
            "reportlab>=4.0.0",
            "python-docx>=0.8.11",
            "openpyxl>=3.1.0",
            "jinja2>=3.1.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-qt>=4.2.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "bolt-studio=bolt_analysis_studio.gui:main",
        ],
        "gui_scripts": [
            "bolt-studio-gui=bolt_analysis_studio.gui:main",
        ],
    },
)
