from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mfs-memory",
    version="1.0.0.0",  # V1.0.0.0 正式版 - C/C++/SQLite 全面优化
    author="main (管家)",
    author_email="main@mfs-memory.ai",
    description="Memory File System V1.0.0.0 - AI 记忆的 Git + NTFS (全面优化版)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mfs-memory",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "mfs-check-install=mfs.cli.install_check:main",
            "mfs-version=mfs.cli.version:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",  # 正式版
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "pytest-asyncio>=0.23",
            "flake8>=6.0",
            "black>=23.0",
        ],
    },
)
