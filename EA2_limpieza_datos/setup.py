from setuptools import find_packages, setup


setup(
    name="ea2-limpieza-datos",
    version="1.0.0",
    description="Preprocesamiento y limpieza de los datos obtenidos en la EA1",
    packages=find_packages(),
    install_requires=["pandas", "openpyxl"],
)

