from setuptools import setup, find_packages

setup(
    name="mazespace",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pygame",
        "PyOpenGL",
        "numpy",
        "noise"
    ],
    author="Antigravity",
    description="A simple 3D rendering library for drones and shapes.",
)
