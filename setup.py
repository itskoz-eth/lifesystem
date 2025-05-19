from setuptools import setup, find_packages

setup(
    name="life_system",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "SQLAlchemy==2.0.27",
        "PyQt5==5.15.10",
        "pandas==2.2.0",
        "python-dateutil==2.8.2",
        "pytz==2024.1",
    ],
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive life management system",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/life_system",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 