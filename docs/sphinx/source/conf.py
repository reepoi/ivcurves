# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

# make repo base directory visible to Sphinx
sys.path.insert(0, os.path.abspath('../../../'))
# make contents of hidden folder .github visible to Sphinx
sys.path.insert(0, os.path.abspath('../../../.github'))
sys.path.insert(0, os.path.abspath('.'))

import site_data

# -- Project information -----------------------------------------------------

project = 'ivcurves'
copyright = '2022, ivcurves Development Team'
author = 'ivcurves Development Team'

# The full version, including alpha/beta/rc tags
release = '1.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.autodoc',
    'sphinx.ext.mathjax',
    'sphinx.ext.intersphinx',
    'sphinx.ext.extlinks',
    'sphinx.ext.napoleon',
    'sphinx.ext.githubpages',
    'sphinxcontrib.datatemplates',
    'sphinxcontrib.autoprogram',
    'sphinxcontrib.mermaid'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

html_additional_pages = {
    'jsonschema': 'jsonschema.html'
}

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'pydata_sphinx_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_css_files = [
    'https://cdn.datatables.net/1.13.1/css/jquery.dataTables.min.css'
]

html_js_files = [
    'https://cdn.datatables.net/1.13.1/js/jquery.dataTables.min.js',
    'datatables/setup.js' # helper script to create the DataTables
]

html_theme_options = {
    'left_sidebar_end': []
}

html_sidebars = {
    'scoreboard': [],
    'test_cases': [],
    'participating': [],
    'jsonschema': []
}

html_context = {
    'scoreboard': {
        'table_rows': site_data.scoreboard_table_rows()
    },
    'test_cases': {
        'test_case_data': site_data.test_set_name_to_parameters_and_image()
    }
}

# extlinks alias
extlinks = {
    'pull': ('https://github.com/cwhanse/ivcurves/pull/%s', '#%s'),
    'ghuser': ('https://github.com/%s', '%s')
}

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'pvlib': ('https://pvlib-python.readthedocs.io/en/stable/', None),
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/reference/', None),
    'pandas': ('https://pandas.pydata.org/pandas-docs/stable', None),
    'matplotlib': ('https://matplotlib.org/stable', None),
}


from docutils import nodes

try:
    # Available from Sphinx 1.6
    from sphinx.util.logging import getLogger
except ImportError:
    from logging import getLogger

log = getLogger(__name__)


def build_table(tabledata):
    """
    References
    ----------
    .. [1] https://github.com/docutils/docutils/blob/3b53ded52bc439d8068b6ecb20ea0a761247e479/docutils/docutils/parsers/rst/states.py#L1793

    .. [2] https://github.com/docutils/docutils/blob/master/docutils/docutils/parsers/rst/tableparser.py#L90
    """
    # colwidths: the length of the longest cell data in a column
    colwidths, headrows, bodyrows = tabledata
    table = nodes.table()
    table['classes'] += ['colwidths-auto']
    tgroup = nodes.tgroup(cols=len(colwidths))
    table += tgroup
    for colwidth in colwidths:
        colspec = nodes.colspec(colwidth=colwidth)
        tgroup += colspec
    if headrows:
        thead = nodes.thead()
        tgroup += thead
        for row in headrows:
            thead += build_table_row(row)
    tbody = nodes.tbody()
    tgroup += tbody
    for row in bodyrows:
        tbody += build_table_row(row)
    return table


def build_table_row(rowdata):
    """
    References
    ----------
    .. [1] https://github.com/docutils/docutils/blob/3b53ded52bc439d8068b6ecb20ea0a761247e479/docutils/docutils/parsers/rst/states.py#L1819

    .. [2] https://github.com/docutils/docutils/blob/master/docutils/docutils/parsers/rst/tableparser.py#L90
    """
    row = nodes.row()
    for cell in rowdata:
        if cell is None:
            continue
        morerows, morecols, offset, cellblock = cell
        attributes = {}
        if morerows:
            attributes['morerows'] = morerows
        if morecols:
            attributes['morecols'] = morecols
        entry = nodes.entry(**attributes)
        entry += nodes.Text(cellblock[0])
        row += entry
    return row


def process_external_version_warning_banner(app, doctree, fromdocname):
    """
    Add warning banner for external versions in every page.

    If the version type is external this will show a warning banner
    at the top of each page of the documentation.
    """
    # Sphinx itself always emits this with a document node,
    # but extensions can also call `resolve_references` with other types
    # of nodes, we don't want to inject the banner in those.
    # Details:
    # - https://github.com/readthedocs/readthedocs-sphinx-ext/issues/113
    # - https://github.com/readthedocs/readthedocs-sphinx-ext/pull/114
    if not isinstance(doctree, nodes.document):
        return

    # Only run for documents under the submissions path
    if not fromdocname.startswith('submissions'):
        return

    # Ignore the index pages
    if fromdocname.endswith('index'):
        return

    print(f'HERE @ {fromdocname}')

    prose = build_table((
        [3, 3, 3],
        [[
            (0, 0, 0, ['A']),
            (0, 0, 0, ['B']),
            (0, 0, 0, ['C']),
        ]],
        [[
            (0, 0, 0, ['a']),
            (0, 0, 0, ['b']),
            (0, 0, 0, ['c']),
        ]]
    ))

    warning_node = nodes.warning(prose, prose)
    doctree.insert(0, warning_node)
    download_pr_overall_scores()


import zipfile
import requests
import pandas as pd
import ivcurves.utils as utils
GITHUB_API_URL = 'https://api.github.com/repos'
def download_pr_overall_scores():
    owner = 'reepoi'
    repo = 'ivcurves'
    pr_num = '106'

    pr = requests.get(f'{GITHUB_API_URL}/{owner}/{repo}/pulls/{pr_num}').json()
    author = pr['user']['login']
    ref, sha = pr['head']['ref'], pr['head']['sha']

    workflows = [
        w for w in
        requests.get(f'{GITHUB_API_URL}/{owner}/{repo}/actions/runs?actor={author}&head_sha={sha}').json()['workflow_runs']
        if w['name'] == 'Score submission'
    ]
    workflow = workflows[0]
    run_id = workflow['id']

    artifacts = [
        a for a in
        requests.get(f'{GITHUB_API_URL}/{owner}/{repo}/actions/runs/{run_id}/artifacts').json()['artifacts']
        if a['name'] == 'overall_scores.csv'
    ]
    artifact = artifacts[0]
    download_url = artifact['archive_download_url']

    download = requests.get(download_url, headers={'Authorization': 'Bearer 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'})
    breakpoint()
    with open(utils.DOCS_DIR / 'overall_scores.zip', 'wb') as f:
        f.write(download.text)

    with zipfile.ZipFile(utils.DOCS_DIR / 'overall_scores.zip', 'r') as f:
        f.extractall(utils.DOCS_DIR)

    overall_scores = pd.read_csv(utils.DOCS_DIR / 'overall_scores.csv', dtype={'test_set': str, 'score': utils.mp.mpmathify})


def setup(app):
    app.connect('doctree-resolved', process_external_version_warning_banner)
