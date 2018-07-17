try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    description="Skyfolk - Social network project",
    author="Adrian Carayol",
    author_email="adriancarayol@gmail.com",
    url="https://skyfolk.jfrog.io/skyfolk/api/pypi/pypi",
    version="1",
    install_requires=["nose",],
    packages=["about","account", "publications"],
    name="Skyfolk",
)
