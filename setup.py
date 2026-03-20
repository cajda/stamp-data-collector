from setuptools import setup

setup(
    name="stamp-data-collector",
    version="2.0",
    description="Desktop application for managing a personal stamp collection",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="tomca",
    python_requires=">=3.8",
    py_modules=["stamp_collector"],
    install_requires=[
        "Pillow>=9.0",
    ],
    data_files=[
        ("", ["countries.json"]),
    ],
    entry_points={
        "console_scripts": [
            "stamp-collector=stamp_collector:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Tk",
        "Topic :: Desktop Environment",
    ],
)
