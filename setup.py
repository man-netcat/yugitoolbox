from setuptools import find_packages, setup

# Read requirements from requirements.txt file
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="yugitoolbox",
    version="1.0",
    packages=find_packages(),
    install_requires=requirements,
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
