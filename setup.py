#!/usr/bin/env python3
"""
FANZA同人出版用モザイクツール
エンジニア向けCLIアプリケーション
"""

from setuptools import setup, find_packages
import os

# READMEファイルの読み込み
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# requirements.txtの読み込み
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="fanza-mosaic-tool",
    version="2.0.0",
    author="AI Assistant",
    description="FANZA隠蔽処理規約準拠のモザイクツール",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/nsdayo12311231-cmyk/fanza-mosaic-tool",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
    python_requires=">=3.9",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "fanza-mosaic=fanza_mosaic_tool.cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "fanza_mosaic_tool": ["config/*.yaml"],
    },
    keywords="mosaic, image-processing, fanza, mediapipe, opencv",
    project_urls={
        "Bug Reports": "https://github.com/nsdayo12311231-cmyk/fanza-mosaic-tool/issues",
        "Source": "https://github.com/nsdayo12311231-cmyk/fanza-mosaic-tool",
    },
)
