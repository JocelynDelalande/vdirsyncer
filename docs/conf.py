# -*- coding: utf-8 -*-

import sys
import os

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']

source_suffix = '.rst'
master_doc = 'index'

project = u'vdirsyncer'
copyright = u'2014, Markus Unterwaditzer'

import pkg_resources
try:
    # The full version, including alpha/beta/rc tags.
    release = pkg_resources.require('vdirsyncer')[0].version
except pkg_resources.DistributionNotFound:
    print('To build the documentation, the distribution information of'
          'vdirsyncer has to be available. Run "setup.py develop" to do'
          'this.')
    sys.exit(1)

del pkg_resources

version = '.'.join(release.split('.')[:2])  # The short X.Y version.

exclude_patterns = ['_build']

pygments_style = 'sphinx'
html_theme = 'default'

html_static_path = ['_static']
htmlhelp_basename = 'vdirsyncerdoc'

latex_elements = {}
latex_documents = [
    ('index', 'vdirsyncer.tex', u'vdirsyncer Documentation',
     u'Markus Unterwaditzer', 'manual'),
]

man_pages = [
    ('index', 'vdirsyncer', u'vdirsyncer Documentation',
     [u'Markus Unterwaditzer'], 1)
]

texinfo_documents = [
    ('index', 'vdirsyncer', u'vdirsyncer Documentation',
     u'Markus Unterwaditzer', 'vdirsyncer', 'One line description of project.',
     'Miscellaneous'),
]
