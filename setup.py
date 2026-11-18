from setuptools import setup, find_packages

setup(
    name='lab4-backend',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'Flask>=3.0.0',
        'Flask-SQLAlchemy>=3.1.0',
        'PyMySQL>=1.1.0',
        'cryptography>=42.0.0',
        'PyYAML>=6.0.0',
    ],
    author='Matvii Ivkov',
    description='Lab 4 Back-End Flask Project with MySQL integration for soilsense_db',
)
