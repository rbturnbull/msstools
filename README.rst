================================================================
MSS Tools
================================================================

.. start-badges

|testing badge| |coverage badge| |docs badge| |black badge|

.. |testing badge| image:: https://github.com/rbturnbull/msstools/actions/workflows/testing.yml/badge.svg
    :target: https://github.com/rbturnbull/msstools/actions

.. |docs badge| image:: https://github.com/rbturnbull/msstools/actions/workflows/docs.yml/badge.svg
    :target: https://rbturnbull.github.io/msstools
    
.. |black badge| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    
.. |coverage badge| image:: https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/rbturnbull/40d96fabbe08e596d6cc876f8f40c1f9/raw/coverage-badge.json
    :target: https://rbturnbull.github.io/msstools/coverage/
    
.. end-badges

.. start-quickstart

Tools for Managing the Manuscripts of Chrysostom’s Homilies on Romans


Installation
==================================

Install using pip:

.. code-block:: bash

    pip install git+https://github.com/rbturnbull/msstools.git


Command Line Usage
==================================


See available commands with:

.. code-block:: bash

    msstools --help

split-image
^^^^^^^^^^^

**Description:**  
Split image files into left and right parts (typically recto and verso pages), with optional right-to-left direction and overlap.

**Arguments:**

- ``prefix``: Path to the output prefix for split images.
- ``images``: One or more image files to be split.
- ``--rtl``: (Optional) Split images in right-to-left direction.
- ``--overlap``: (Optional) Overlap percentage between split images (default: 10).
- ``--skip``: (Optional) Number of pages to skip before splitting.
- ``--force``: (Optional) Overwrite existing files if they exist.

**Example:**

.. code-block:: bash

    msstools split-image output_dir/page img001.jpg img002.jpg --rtl --overlap 20

remove-accents
^^^^^^^^^^^^^^

**Description:**  
Remove accents from a UTF-8 text file and save the cleaned version to a new file.

**Arguments:**

- ``input_file``: Path to the input text file.
- ``output_file``: Path to the output text file with accents removed.

**Example:**

.. code-block:: bash

    msstools remove-accents input.txt output.txt

number-sentences
^^^^^^^^^^^^^^^^

**Description:**  
Number ``<S>`` sentence tags within ``<P>`` paragraph blocks in an XML or structured text file.

**Arguments:**

- ``input_file``: Path to the input text file.
- ``output_file``: Path to the output file with numbered sentence tags.

**Example:**

.. code-block:: bash

    msstools number-sentences homily1.xml homily1_numbered.xml

count-greek-chars
^^^^^^^^^^^^^^^^^

**Description:**  
Count the number of Greek characters in a set of homily text files and generate a plot showing the results. Optionally display or save the plot.

**Arguments:**

- ``filename_prefix``: Prefix used to construct the filenames of the homily files.
- ``homily_count``: Number of homilies to process.
- ``--warning-stdev``: (Optional) Standard deviation threshold for highlighting outliers (default: 1.8).
- ``--output``: (Optional) Path to save the plot as an image.
- ``--show``: (Optional) Show the plot in a window (default: False).

**Example:**

.. code-block:: bash

    msstools count-greek-chars homily 33 --output greek_chars.png --show

compare-counts
^^^^^^^^^^^^^^

**Description:**  
Compare the Greek character counts between two sets of homily transcriptions and generate a plot showing where the comparison text has significantly more characters than the base.

**Arguments:**

- ``base_prefix``: Prefix for the base homily files.
- ``comparison_prefix``: Prefix for the comparison homily files.
- ``output_path``: Path to save the resulting plot.
- ``--start-homily``: (Optional) First homily number to compare (default: 0).
- ``--end-homily``: (Optional) Last homily number to compare (default: 32).
- ``--threshold``: (Optional) Character difference threshold that triggers a warning (default: 50).

**Example:**

.. code-block:: bash

    msstools compare-counts Migne_H Saba20_H Migne_vs_Saba20.png --threshold 40

csv-to-tei
^^^^^^^^^^

**Description:**  
Convert a CSV file of variant readings into TEI XML format. Optionally limit readings and add dates from a separate file.

**Arguments:**

- ``input_csv``: Path to the input CSV file containing readings.
- ``output_xml``: Path to the TEI XML output file.
- ``--dates``: (Optional) Path to a file containing date information.
- ``--max-readings``: (Optional) Maximum number of readings to process at each variation unit (default: 0 = no limit).

**Example:**

.. code-block:: bash

    msstools csv-to-tei readings.csv output-tei.xml --dates dates.csv --max-readings 10


.. end-quickstart


Credits
==================================

.. start-credits

- `Robert Turnbull <https://robturnbull.com>`_ 
- Peter Montoro


.. end-credits

