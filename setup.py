from setuptools import setup, find_namespace_packages

# Load the requirements from the requirements.txt file
with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

# Read the README.md file for the long description
with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="reclaim-sdk",
    version="0.4.0",
    description="Unofficial Reclaim.ai Python API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/llabusch93/reclaim-sdk",
    author="Laurence Lars Labusch",
    author_email="llabusch@labusch-it.com",
    license="MIT",
    packages=find_namespace_packages(),
    zip_safe=False,
    scripts=[],
    python_version=">=3.6",
    install_requires=requirements,
)
