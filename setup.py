from setuptools import setup

setup(name='lightfield',
      version='0.1',
      description='A library for communicating with the .NET Lightfield server component created by William Talmadge and used in the Spin Optics group in the University of Utah physics department',
      url='https://github.com/willtalmadge/Lightfield',
      author='William Talmadge',
      author_email='willtalmadge@gmail.com',
      license='MIT',
      packages=[
          'request',
      ],
      install_requires=[
            'numpy',
            'flask'
      ],
      zip_safe=False)