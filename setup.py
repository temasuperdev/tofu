"""Setup configuration for the project."""
from setuptools import setup, find_packages

setup(
    name="demo-app",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask>=2.3.0",
        "werkzeug>=2.3.0",
        "gunicorn>=20.1.0",
        "python-dotenv>=1.0.0",
    ],
)
