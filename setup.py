from setuptools import find_packages, setup


def readme():
    with open("README.md", "r") as file:
        return file.read()


def requirements():
    with open("requirements/requirements.txt") as file:
        return file.read().splitlines()


setup(
    name="todo-ms-client",
    version="0.1.0",
    description="Unofficial Python library for MS ToDo API",
    long_description=readme(),
    long_description_content_type="text/markdown",
    install_requires=requirements(),
    url="https://github.com/kam193/todo-ms-client",
    author="Kamil Mańkowski",
    author_email="gh.welcome@tools.kam193.eu",
    license="MIT",
    packages=find_packages(exclude=["*tests*"]),
    zip_safe=False,
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
