from setuptools import find_packages, setup

setup(
    name="dawn",
    version="0.1.0",
    packages=find_packages(include=["core", "core.*", "llm", "llm.*", "utils", "utils.*"]),
    install_requires=[
        "openai",
        "python-dotenv",
        "pytest",
    ],
)
