from setuptools import setup, find_packages

from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_suite = "tests"
    def run_tests(self):
        import pytest
        pytest.main(self.test_args)

setup(
    name='generic_anova',
    version='1.0.0',
    packages=find_packages(),
    url='',
    license='',
    author='tsasaki',
    author_email='',
    description='',
    install_requires=[
        "tornado==4.5.2",
        "RPi.GPIO",
        "requests>=2.10.0",
    ],
    tests_require=[
        "pytest",
        "freezegun",
    ],
    cmdclass={'pytest': PyTest},
    test_suite='tests',
    entry_points="""
    [console_scripts]
    ganova=generic_anova.app:main
    """
)
