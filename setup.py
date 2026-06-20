#!/usr/bin/env python3
"""
GitHub Profile Analyzer - Setup Script
설치 및 설정 도우미
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="github-profile-analyzer",
    version="1.0.0",
    author="GitHub Profile Analyzer Team",
    description="GitHub 프로필 분석 도구 - 커밋, 코드량, 언어 분포 통계",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/gitscraper",
    py_modules=[
        "github_scraper",
        "github_scraper_cli",
        "advanced_analyzer",
        "visualizer",
        "run_analysis"
    ],
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "github-analyzer=github_scraper:main",
            "github-analyzer-cli=github_scraper_cli:main",
            "github-analyzer-advanced=advanced_analyzer:main",
            "github-analyzer-viz=visualizer:main",
            "github-analyzer-full=run_analysis:main",
        ],
    },
)
