import setuptools
from setuptools import find_packages
import os
import io

# Current directory
here = os.path.abspath(os.path.dirname(__file__))

def get_requirements():
    """
    Reads and parses the requirements.txt file to get package dependencies.
    
    Returns:
        list: List of package requirements
    """
    requirements_path = os.path.join(here, 'requirements.txt')
    with open(requirements_path, 'r') as f:
        requirements = f.read().splitlines()
    
    # Filter out comments and empty lines
    requirements = [line.strip() for line in requirements 
                   if line.strip() and not line.strip().startswith('#')]
    
    return requirements

def read(filename):
    """
    Reads the content of a file, typically used for README.md.
    
    Args:
        filename (str): Name of the file to read
        
    Returns:
        str: Content of the file
    """
    with io.open(os.path.join(here, filename), 'r', encoding='utf-8') as f:
        return f.read()

setuptools.setup(
    name="indivillage-backend",
    version="0.1.0",
    description="Backend API for IndiVillage.com website",
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    author="IndiVillage Development Team",
    author_email="dev@indivillage.com",
    url="https://github.com/indivillage/indivillage-website",
    packages=find_packages(exclude=['tests*', 'scripts*']),
    python_requires=">=3.10",
    install_requires=get_requirements(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    entry_points={
        'console_scripts': [
            'indivillage-backend=app.main:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)