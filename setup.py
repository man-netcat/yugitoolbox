from setuptools import find_packages, setup

setup(
    name="yugitoolbox",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4==4.12.2",
        "fake_useragent==1.4.0",
        "jaro_winkler==2.0.3",
        "pandas==2.1.4",
        "Pillow==10.1.0",
        "Requests==2.31.0",
        "setuptools==65.5.0",
    ],
    package_data={
        "yugitoolbox": [
            "assets/**",
            "sql/*.sql",
        ],
    },
    entry_points={
        "console_scripts": [],
    },
    description="Yu-Gi-Oh! Database Wrapper",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
