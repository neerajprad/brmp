from setuptools import find_packages, setup

setup(name='brmp',
      packages=find_packages(),
      install_requires=[
        'pandas',
        'pyro-ppl>=0.5.1',
        'numpyro>=0.2.1',
      ],
      extras_require={
          'test': ['flake8', 'pytest'],
          'docs': ['sphinx', 'sphinx-rtd-theme'],
      })
