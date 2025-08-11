from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="meetspot",
    version="1.0.0",
    author="MeetSpot Team",
    author_email="Johnrobertdestiny@gmail.com",
    description="Intelligent Meeting Point Recommendation System - Find the Perfect Place for Every Gathering",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JasonRobertDestiny/MeetSpot",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.115.0",
        "uvicorn>=0.34.0",
        "pydantic>=2.10.0",
        "aiohttp>=3.9.0",
        "aiofiles>=24.1.0",
        "toml>=0.10.2",
        "loguru>=0.7.3",
        "httpx>=0.27.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.3.0",
            "pytest-asyncio>=0.25.0",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Scientific/Engineering :: GIS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "meetspot=simple_server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.html", "*.css", "*.js", "*.toml", "*.md"],
    },
)
