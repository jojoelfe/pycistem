# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pycistem', 'pycistem.core', 'pycistem.programs']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pycistem',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Johannes Elferich',
    'author_email': 'jojotux123@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
