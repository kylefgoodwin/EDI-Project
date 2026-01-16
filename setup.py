from setuptools import setup, find_packages

setup(
    name="edi_project",
    version="0.0.1",
    description="EDI Project - X12 parser and services",
    packages=find_packages(exclude=("tests", "edi-desktop-app", "venv")),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn[standard]",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart",
        "google-genai",
    ],
)
