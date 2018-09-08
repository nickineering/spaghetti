from setuptools import setup

setup(name='spaghetti-graph',
      version='1.0.1',
      description='Graph function level Python dependencies to understand and fix spaghetti code',
      url='https://github.com/nferrara100/spaghetti',
      author='Nicholas Ferrara',
      author_email='nferrara100@gmail.com',
      license='MIT',
      packages=['spaghetti'],
      install_requires=['networkx', 'matplotlib'],
      dependency_links=['https://github.com/nferrara100/spaghetti/tree/master'],
      entry_points={
          'console_scripts': ['spaghetti=spaghetti.command_line:main'],
      },
      zip_safe=False)
