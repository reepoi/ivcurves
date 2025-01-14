.. _participating:


How to Participate
==================


Submission Workflow
-------------------

These are the steps to make a submission as a competitor.
You can make multiple submissions, and each will be a separate entry on the leaderboard.

#. Create a fork of the ivcurves repository.
#. Create a new folder ``submissions/<your_GitHub_username>``.
   This folder will store all of the files you create.
#. Write or copy your submission's code inside ``submissions/<your_GitHub_username>``.
#. Create a file ``pr_config.json`` with three entries:

   .. code-block:: json

      {
          "RUN_SCORER": true,
          "REQUIREMENTS": "<path_to_requirements>.txt",
          "SUBMISSION_MAIN": "<path_to_submission_entrypoint>.py"
      }

   ``REQUIREMENTS`` and ``SUBMISSION_MAIN`` must be paths relative to ``submissions/<your_GitHub_username>``.
   For example, if your Pip requirements file is located at ``submissions/<your_GitHub_username>/requirements.txt``, ``REQUIREMENTS`` should be ``./requirements.txt``.
#. Push your changes to your fork, and then GitHub will automatically run the scorer with your code.
   When it is finished, you will see either a green check mark or red x icon next to your commit indicating whether the scorer succeeded or not.
   Click on the icon  to see the results of the scorer.
   The scorer will also provide a CSV file containing your code's score.

   .. note::
      GitHub will execute your the entrypoint of your submission ``SUBMISSION_MAIN`` from the same folder that contains it.
      Therefore, your code may use relative paths when reading and writing files.

#. When you are ready, and there is a green check mark next to your latest commit, create a pull request into ``cwhanse/ivcurves/main``.
   GitHub will again automatically run and score your code.
   An ivcurves maintainer will be notified of your pull request.
#. After an ivcurves maintainer reviews and approves your pull request, it will be merged.
   GitHub will post your GitHub username and score to the leaderboard.

Submission Workflow Diagram
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. mermaid::

   sequenceDiagram
       participant Competitor
       participant GitHub Actions
       participant ivcurves Maintainer

       activate Competitor
       Note over Competitor: Forks ivcurves repository.
       Note over Competitor: Creates folder submissions/<your_GitHub_username> to put their files into.
       Note over Competitor: Creates pr_config.json.
       Note over Competitor: Writes code for submission.

       Competitor->>GitHub Actions: Pushes code to fork on GitHub
       deactivate Competitor
       activate GitHub Actions
       Note over GitHub Actions: Reads pr_config.json and scores submission.
       GitHub Actions->>Competitor: Reports results with CSV of scores
       deactivate GitHub Actions

       Competitor->>GitHub Actions: Creates pull request
       activate GitHub Actions
       Note over GitHub Actions: Reads pr_config.json and scores submission code.
       GitHub Actions->>Competitor: Reports results with CSV of scores
       GitHub Actions->>ivcurves Maintainer: Notifies of pull request
       deactivate GitHub Actions
       activate ivcurves Maintainer
       Note over ivcurves Maintainer: Reviews pull request.
       ivcurves Maintainer->>GitHub Actions: Merges competitor's pull request
       activate GitHub Actions
       deactivate ivcurves Maintainer
       GitHub Actions->>Competitor: Notifies of pull request merge
       Note over GitHub Actions: Records submission's score in database.
       Note over GitHub Actions: Updates leaderboard and submission documentation.
       deactivate GitHub Actions


Submission Requirements
-----------------------

Your code is run with the command ``python3 <filename_of_submission_entrypoint>.py`` from the folder containing the entrypoint of your submission.

**When your code runs, it must:**

#. Read all of the IV curve JSON test sets in the ``test_sets`` folder. See `Reading IV Curve JSON Test Sets`_.
#. For each test set, write a CSV file containing fitted parameters for every IV curve in the test set. See `Writing Test Set Results to CSV Files`_.

Reading IV Curve JSON Test Sets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Each JSON test set follows the :ref:`jsonschema`.
Here is an example:

.. code-block::

  {
    "Manufacturer": "",
    "Model": "",
    "Serial Number": "",
    "Module ID": "",
    "Description": "",
    "Material": "",
    "cells_in_series": 72,
    "IV Curves": [
      {
        "Index": 1,
        "Voltages": [
          "0.0",
          ...
        ],
        "Currents": [
          "0.9996667777132812",
          ...
        ],
        "diode_voltage": [
          "0.09996667777132812",
          ...
        ],
        "v_oc": "39.7481074783976643",
        "i_sc": "0.9996667777132812",
        "v_mp": "33.9368943991155301",
        "i_mp": "0.8461238606639279",
        "p_mp": "28.7148161079236649",
        "Temperature": "298.15",
        "Irradiance": null,
        "Sweep direction": "",
        "Datetime": "1970-01-01T00:00:00Z"
      },
      ...
    ]
  }

Under the ``"IV Curves"`` key is a list of IV curve data sets each with an ``"Index"`` value.
The ``"Index"`` value is the test case number of the test set.

The decimal numbers in each test case are calculated at a higher precision than what a 64-bit floating point number can store.
To be sure that precision is not lost unintentionally when reading the JSON, the numbers are stored in strings.
The competitor must decide how to parse these numbers in their submission.
Here are some options:

#. Parse the strings containing a number into a Python :py:class:`float`.
   Any precision that cannot be stored in a 64-bit floating point number will be lost.
#. Use an arbitrary precision math library to parse the strings containing a number.
   The library `mpmath`_ was used to calculate the IV curve data in these test sets.

   .. _mpmath: https://mpmath.org/

JSON test sets may be added after you submit your code, so it must not rely on their filename.
Here is Python code that may be useful for getting a set of all the JSON filenames in ``test_sets`` dynamically:

.. code-block:: python

    # these modules are part of the Python standard library
    import json
    import pathlib

    # these modules are installed
    import numpy as np
    import pandas as pd


    def get_test_set_filepaths():
        """
        Returns a sorted list of pathlib.Path objects pointing to the JSON test set
        files. pathlib.Path objects can be passed directly to Python's ``open``
        function to open the JSON file.

        Returns
        -------
            A list.
        """
        path_to_test_sets = pathlib.Path.cwd() / '..' / '..' / 'test_sets'
        file_entries = list({path_to_test_sets / f'{entry.stem}.json'
                             for entry in path_to_test_sets.iterdir()
                             if entry.is_file()})
        file_entries.sort()
        return file_entries


    def get_test_set_name(filepath):
        """
        Gets a test set filename from a filepath.

        Parameters
        ----------
        filepath : pathlib.Path
            A filepath pointing to a JSON test set file.

        Returns
        -------
            The test set name given a pathlib.Path object pointing to a JSON
            test set file.
        """
        return filepath.stem


    def json_file_to_df(filepath):
        """
        Creates a pandas DataFrame from an IV Curve JSON file.
        All of the numerical values stored as strings in the JSON as parsed to
        np.float64.

        Parameters
        ----------
        filepath : pathlib.Path
            A Path object pointing to the JSON file.

        Returns
        -------
            A pandas DataFrame.
        """
        curves_metadata = pd.read_json(filepath)
        curves = pd.DataFrame(curves_metadata['IV Curves'].values.tolist())
        curves['cells_in_series'] = curves_metadata['cells_in_series']

        # set up index
        curves['Index'] = curves['Index'].astype(int)
        curves = curves.set_index('Index')

        # convert Voltages, Currents, and diode_voltage from string arrays to
        # float arrays. This truncates from precise values to 64-bit precision.
        is_array = ['Voltages', 'Currents', 'diode_voltage']
        curves[is_array] = curves[is_array].applymap(
            lambda a: np.asarray(a, dtype=np.float64)
        )

        # convert from string to float
        is_number = ['v_oc', 'i_sc', 'v_mp', 'i_mp', 'p_mp', 'Temperature']
        curves[is_number] = curves[is_number].applymap(np.float64)

        return curves


    def json_file_to_dict(filepath):
        """
        Returns a Python dict of the contents of a JSON file.

        Parameters
        ----------
        filepath : pathlib.Path
            The filepath pointing to a JSON file.

        Returns
        -------
            A Python dict.
        """
        with open(filepath, 'r') as file:
            return json.load(file)

Writing Test Set Results to CSV Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For each JSON test set ``<test_set_name>.json`` in ``test_sets``, your code must write a CSV file ``<test_set_name>.csv`` **in the folder containing the entrypoint of your submission.**
Each CSV file must have these columns:

.. datatemplate:nodata::

  {{ make_list_table([
        'Index',
        'photocurrent',
        'saturation_current',
        'resistance_series',
        'resistance_shunt',
        'n',
        'cells_in_series'
     ],
     [['#','#','#','#','#','#','#']],
     title='<test_set_name>.csv')
  }}

The column ``n`` is the diode factor.

Each row of the CSV file will contain your fitted parameters for each test case in its corresponding test set.
The script that scores your submission will read your CSV file and use an arbitrary precision math library to parse your fitted parameters.

Testing Your Submission
-----------------------

The Python scripts used to score your submission are available for you to run locally.
For example, you may run ``ivcurves/compare_curves.py`` to score your fitted parameters for a test set.

To run ``ivcurves/compare_curves.py`` for all test sets, run the command

.. code-block:: bash

   python3 ivcurves/compare_curves.py folder/containing/your/CSV/files/ --csv-ouput-path folder/to/write/your/scores/

To run ``ivcurves/compare_curves.py`` for a single test set ``<test_set>.json``, run the command

.. code-block:: bash

   python3 ivcurves/compare_curves.py folder/containing/your/CSV/files/ --test-set <test_set> --csv-ouput-path folder/to/write/your/scores/
   # the file extension of the --test-set argument is NOT included

See the `Compare Curves documentation <reference/compare_curves.html>`_ for more information.

Documenting Your Submission
---------------------------

These steps will cover how to add documentation to your submission, and display it on the ivcurves Submissions page.
The ivcurves documentation uses numpy-sytle docstrings, so your module and function docstrings should follow that style.
In your docstrings, you may create links to external sites to help describe or contextualize your code using this Sphinx rst directive:

   .. code-block:: rst

      Link to an `external site`_.

      .. _external site: <url>

      ..
         Example:

      Link to `Sphinx documentation`_.

      .. _Sphinx documentation: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#hyperlinks

After writing docstrings for your submission, you need to generate Sphinx .rst files for your submission using a command line program provided in ivcurves.
First, ensure that none of your submission's Python files are named ``index.py`` because ``index`` is reserved for the Sphinx documentation.
To generate the .rst files, run the command

   .. code-block:: bash

      python3 docs/sphinx/source/gen_submission_rst.py submissions/<your_GitHub_username>/pr_config.json

It will print out a file tree of the .rst files created.
The .rst files named after a Python file in your submission will have contents similar to

   .. code-block:: rst
      :emphasize-lines: 1

      <your_py_filename>
      ==================

      .. automodule:: submissions.<your_GitHub_username>.<your_py_filename>
         :members:

The highlighted line above is the title of the documentation page for that Python file.
You may change it, but make sure your entire title is underlined by the equal signs on the line below.
If you change the title of the documentation page for ``SUBMISSION_MAIN``, this title will be displayed on the leaderboard under the **Method Name** column.

