
Amber
=====

Supported museums:


* Minneapolis Institute of Art
* Guggenheim

Installation
------------

.. code-block::

   git clone https://github.com/GOATS2K/amber.git
   python setup.py install --user

Run ``amber config`` to edit your config.

Config
------

**Filename template**

The file name template supports the following keys:

.. code-block::

   source
   artist
   title
   portfolio
   credits
   country
   dated
   resolution

Template example: ``{artist} - {title} ({dated}) [{resolution}]``

Generates: ``Vincent van Gogh - Olive Trees (1889) [10501x8342]``

Usage
-----

.. code-block::

   Usage: amber [OPTIONS] COMMAND [ARGS]...

   Options:
     --help  Show this message and exit.

   Commands:
     config    Edit configuration file
     download  Download an image by ID
     search    Search museums for images

Run ``--help`` on each command for more details.
