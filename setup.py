from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='spaghetti-graph',
    version='1.0.1',
    description='Graph function level Python dependencies to understand and fix spaghetti code',
    long_description=readme(),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5'
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Debuggers',
    ],
    keywords='dependency graphs',
    url='https://github.com/nferrara100/spaghetti',
    author='Nicholas Ferrara',
    author_email='nferrara100@gmail.com',
    license='MIT',
    packages=['spaghetti'],
    install_requires=['networkx', 'matplotlib'],
    entry_points={
        'console_scripts': ['spaghetti=spaghetti.command_line:main'
                            'spaghetti-graph=spaghetti.command_line:main'
                            ],
    },
    test_suite='nose.collector',
    tests_require=['nose', 'nose-cover3'],
    zip_safe=False)
