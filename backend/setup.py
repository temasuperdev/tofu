"""Setup configuration for the project."""
from setuptools import setup, find_packages

setup(
    name="demo-app",
    version="1.0.0",
    packages=find_packages(include=['src', 'src.*']),
    include_package_data=True,
    install_requires=[
        "flask>=2.3.0",
        "werkzeug>=2.3.0",
        "gunicorn>=20.1.0",
        "python-dotenv>=1.0.0",
        "structlog>=24.0.0",
        "python-json-logger>=2.0.7",
        "flask-caching>=2.0.0",
        "redis>=5.0.0",
        "flask-limiter>=3.5.0",
        "marshmallow>=3.19.0",
        "validators>=0.20.0",
        "flasgger>=0.9.7"
    ],
)