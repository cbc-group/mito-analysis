"""
Minimal setup.py to simplify project setup.
"""
from setuptools import find_packages, setup

setup(
    name="mito-analysis",
    version="0.1",
    description="",
    author="Liu, Yen-Ting",
    author_email="ytliu@gate.sinica.edu.tw",
    license="Apache 2.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={"": ["data/*"]},
    install_requires=["numpy", "scipy"],
    zip_safe=True,
    extras_require={
        "denoise": ["six", "keras>=2.1.6", "tqdm", "csbdeep>=0.4.0,<0.5.0"],
        "events": ["pandas"],
    },
)
