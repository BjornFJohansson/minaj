#!/usr/bin/env python
# -*- coding: utf-8 -*-

import versioneer
from setuptools import setup

setup(  name='minaj',
        version=versioneer.get_version()[:5],
        cmdclass=versioneer.get_cmdclass(),
        packages=['minaj'],
        entry_points = { 'console_scripts' : [ 'minaj = minaj.minaj:main'] },
        license='LICENSE',
        description='''Making and uploading conda packages''',
        zip_safe = False,
        keywords = u"conda")







