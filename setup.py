from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="quickdot",
    version="0.2.1",
    author="Kamil Tokarski",
    author_email="kamil@tokarski.xyz",
    description="A small ssg or rather a set of scripts for personal website",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/ktxyz/quickdot/",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "quickdot=quickdot.__main__:main",
        ]
    },
)
