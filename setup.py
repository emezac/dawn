from setuptools import find_packages, setup

setup(
    name="dawn",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai",
        "httpx",
        "python-dotenv",
    ],
)
