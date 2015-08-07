import glob
import os
import platform
import subprocess
import sys

from setuptools import setup, Command, Extension
from setuptools.command.test import test as TestCommand


def define_extensions(file_ext):

    return [Extension("lightfm.lightfm_fast",
                      ['lightfm/lightfm_fast%s' % file_ext],
                      extra_link_args=["-fopenmp"],
                      extra_compile_args=['-fopenmp'])]


def set_gcc():
    """
    Try to find and use GCC on OSX for OpenMP support.
    """

    if 'darwin' in platform.platform().lower():

        gcc_binaries = sorted(glob.glob('/usr/local/bin/gcc-*'))

        if gcc_binaries:
            _, gcc = os.path.split(gcc_binaries[-1])
            os.environ["CC"] = gcc

        else:
            raise Exception('No GCC available. Install gcc from Homebrew '
                            'using brew install gcc.')


class Cythonize(Command):
    """
    Compile the extension .pyx files.
    """

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):

        import Cython
        from Cython.Build import cythonize

        cythonize(define_extensions('.pyx'))


class Clean(Command):
    """
    Clean build files.
    """

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):

        pth = os.path.dirname(os.path.abspath(__file__))

        subprocess.call(['rm', '-rf', os.path.join(pth, 'build')])
        subprocess.call(['rm', '-rf', os.path.join(pth, 'lightfm.egg-info')])
        subprocess.call(['find', pth, '-name', 'lightfm*.pyc', '-type', 'f', '-delete'])
        subprocess.call(['rm', os.path.join(pth, 'lightfm', 'lightfm_fast.so')])


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


set_gcc()


setup(
    name='lightfm',
    version='1.0',
    description='LightFM recommendation model',
    url='https://github.com/lyst/lightfm',
    download_url='https://github.com/lyst/lightfm/tarball/1.0',
    packages=['lightfm'],
    install_requires=['numpy'],
    tests_require=['pytest', 'requests', 'scikit-learn', 'scipy'],
    cmdclass={'test': PyTest, 'cythonize': Cythonize, 'clean': Clean},
    author='Lyst Ltd (Maciej Kula)',
    author_email='data@ly.st',
    license='MIT',
    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: MIT License',
                 'Topic :: Scientific/Engineering :: Artificial Intelligence'],
    ext_modules=define_extensions('.c')
)
