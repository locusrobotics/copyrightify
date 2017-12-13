from setuptools import setup

setup(
    name='copyrightify',
    packages=['copyrightify'],
    version='0.0.2',
    description='Apply copyright/license headers to source files',
    license='BSD',
    author='Paul Bovbel',
    author_email='pbovbel@locusrobotics.com',
    url='https://github.com/locusrobotics/copyrightify',
    install_requires=[
        'Jinja2>=2.9',
        'GitPython>=2.1',
        'PyYaml>=3.12'
    ],
    entry_points={
      'console_scripts': [
          'copyrightify = copyrightify.copyrightify:main'
      ]
    },
    include_package_data=True,
    package_data={'copyrightify': ['config.yaml']},
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Documentation',
    ],
)
