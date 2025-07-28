from setuptools import setup, find_packages

setup(
    name="download-app",
    version="1.0.0",
    py_modules=["download_app"],
    install_requires=[
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "download-app = download_app:main",
        ],
    },
    description="A swift and efficient file downloader for the command line.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/lordvonko/download-app",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

