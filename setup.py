from setuptools import setup, find_namespace_packages

# Load the requirements from the requirements.txt file
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

# Read the README.md file for the long description
with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="reclaimai-sdk",
    version="0.1",
    description="Unofficial Reclaim.ai Python API",
    long_description=long_description,
    url="https://github.com/llabusch93/reclaimai-sdk",
    author="Laurence Lars Labusch",
    author_email="llabusch@labusch-it.com",
    license="MIT",
    packages=find_namespace_packages(),
    zip_safe=False,
    scripts=[],
    python_version=">=3.6",
    install_requires=requirements,
)
