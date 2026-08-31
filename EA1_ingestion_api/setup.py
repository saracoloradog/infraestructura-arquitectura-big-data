from setuptools import find_packages, setup


setup(
    name="ea1-ingestion-api",
    version="1.0.0",
    description="Ingestión de productos desde una API hacia SQLite",
    packages=find_packages(),
    install_requires=["requests", "pandas", "openpyxl"],
)

