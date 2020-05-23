from setuptools import find_packages, setup


def readme():
    with open("README.md", "r") as file:
        return file.read()


def requirements():
    with open("requirements.in") as file:
        return file.read().splitlines()


setup(
    name="todo-ms-client",
    version="0.0.1",
    description="Unofficial Python library for MS ToDo API",
    long_description=readme(),
    long_description_content_type="text/markdown",
    install_requires=requirements(),
    url="https://github.com/kam193/todo-ms-client",
    author="Kamil Mańkowski",
    author_email="kam193@wp.pl",
    license="MIT",
    packages=find_packages(),
    zip_safe=False,
)
