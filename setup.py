# Software License Agreement (proprietary)
#
# \file      setup.py
# \authors   Paul Bovbel <pbovbel@locusrobotics.com>
# \copyright Copyright (c) (2017,), Locus Robotics, All rights reserved.
#
# Unauthorized copying of this file, via any medium, is strictly prohibited.
# Proprietary and confidential.
from setuptools import setup

setup(name='copyrightify',
      packages=['copyrightify'],
      version='0.0.1',
      description='Apply copyright/license headers to source files',
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
