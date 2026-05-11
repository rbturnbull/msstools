================================================================
MSS Tools
================================================================

.. start-badges

|pypi badge| |testing badge| |coverage badge| |docs badge| |black badge| |doi badge|

.. |pypi badge| image:: https://img.shields.io/pypi/v/msstools?color=blue
   :alt: PyPI - Version
   :target: https://pypi.org/project/msstools/

.. |testing badge| image:: https://github.com/rbturnbull/msstools/actions/workflows/testing.yml/badge.svg
    :target: https://github.com/rbturnbull/msstools/actions

.. |docs badge| image:: https://github.com/rbturnbull/msstools/actions/workflows/docs.yml/badge.svg
    :target: https://rbturnbull.github.io/msstools
    
.. |black badge| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    
.. |coverage badge| image:: https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/rbturnbull/40d96fabbe08e596d6cc876f8f40c1f9/raw/coverage-badge.json
    :target: https://rbturnbull.github.io/msstools/coverage/

.. |doi badge| image:: https://www.fdr.uni-hamburg.de/badge/DOI/10.25592/uhhfdm.18367.svg
    :target: https://doi.org/10.25592/uhhfdm.18367
    
.. end-badges

.. start-quickstart

Tools for Managing the Manuscripts.
Derived from Peter Montoro's thesis regarding of Chrysostom’s Homilies on Romans.


Installation
==================================

To install, use the following command:

.. code-block:: bash

    pip install msstools

To install the latest development version, use:

.. code-block:: bash

    pip install -U git+https://github.com/rbturnbull/msstools.git


Command Line Usage
==================================

See available commands with:

.. code-block:: bash

    msstools --help

split-images
^^^^^^^^^^^^

**Description:**  
Split image files into left and right parts (typically recto and verso pages), with optional right-to-left direction, overlap, and flexible naming.

**Arguments:**

- ``prefix``: Path to the output prefix for split images.
- ``images``: One or more image files to be split.
- ``--rtl``: (Optional) Split images in right-to-left direction.
- ``--overlap``: (Optional) Overlap percentage between split images (default: 10).
- ``--skip``: (Optional) Number of images to skip before splitting.
- ``--recto``: (Optional) Recto folio anchor in the form ``FILENAME=FOLIO``. Can be used multiple times.
- ``--force``: (Optional) Overwrite existing output files if they already exist.

**Example (sequential numbering):**

.. code-block:: bash

    msstools split-images output/page img001.jpg img002.jpg --rtl --overlap 20

This will create the following files:

.. code-block:: 
    
    output/page-0.jpg
    output/page-1.jpg
    output/page-2.jpg
    output/page-3.jpg

Skipped images are copied into the same output sequence without a folio
reference. For example, ``--skip 3`` starts with ``page-0.jpg``,
``page-1.jpg``, and ``page-2.jpg``.

**Example (folio references):**

.. code-block:: bash

    msstools split-images output/page img001.jpg img002.jpg img003.jpg --recto img002.jpg=49

This will create the following files:

.. code-block:: 

    output/page-0.jpg
    output/page-1.jpg
    output/page-2.jpg
    output/page-3-49r.jpg
    output/page-4-49v.jpg
    output/page-5-50r.jpg

Everything before the first ``--recto`` anchor has no folio reference. After an
anchor, folio references continue automatically until the next anchor.

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

    msstools number-sentences H1.txt H1_numbered.txt

count-greek-chars
^^^^^^^^^^^^^^^^^

**Description:**  
Count the number of Greek characters in a set of homily text files and generate a plot showing the results. Optionally display or save the plot.

**Arguments:**

- ``filename_prefix``: Prefix used to construct the filenames of the homily files.
- ``--start-homily``: (Optional) First homily number to compare (default: 0).
- ``--end-homily``: (Optional) Last homily number to compare (default: 32).
- ``--warning-stdev``: (Optional) Standard deviation threshold for highlighting outliers (default: 1.8).
- ``--output``: (Optional) Path to save the plot as an image.
- ``--show``: (Optional) Show the plot in a window (default: False unless there is no output).

**Example:**

.. code-block:: bash

    msstools count-greek-chars Jerusalem_PB_Saba_20_copy/Saba20_H --output Saba20-counts.png

compare-counts
^^^^^^^^^^^^^^

**Description:**  
Compare the Greek character counts between two sets of homily transcriptions and optionally generate a plot showing where the comparison text has significantly more characters than the base.

**Arguments:**

- ``base_prefix``: Prefix for the base homily files.
- ``comparison_prefix``: Prefix for the comparison homily files.
- ``--output-svg``: (Optional) Path to save the resulting plot as an SVG.
- ``--start-homily``: (Optional) First homily number to compare (default: 0).
- ``--end-homily``: (Optional) Last homily number to compare (default: 32).
- ``--threshold``: (Optional) Character difference threshold that triggers a warning (default: 50).

**Example:**

.. code-block:: bash

    msstools compare-counts Migne_H Saba20_H --threshold 40

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

To if you use this software in your research, please cite the following article:

Montoro, Peter, and Robert Turnbull. “Tools, Tricks, and Techniques: Managing the Manuscripts of Chrysostom’s Homilies on Romans.” *Comparative Oriental Manuscript Studies Bulletin* 11 (2025): 265–88.
DOI: `10.25592/uhhfdm.18366 <https://doi.org/10.25592/uhhfdm.18366>`_

.. code-block:: bibtex

    @article{msstools,
        author = {Montoro, Peter and Turnbull, Robert},
        title = {{Tools, Tricks, and Techniques: Managing the Manuscripts of Chrysostom’s Homilies on Romans}},
        year = {2025},
        volume = {11},
        pages = {265-288},
        journal = {Comparative Oriental Manuscript Studies Bulletin},
        doi = {10.25592/uhhfdm.18366}
    }

.. end-credits
