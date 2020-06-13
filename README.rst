
Amber
=====

Supported museums:


* Minneapolis Institute of Art
* Guggenheim

Requirements:

* Python 3.7 or higher


Installation
------------

Make sure you're able to run applications installed in your user directory by appending the
folder Python installs packages in to your ``PATH`` environment variable.

On Linux you can add the following string to your shell's respective configuration file (e.g. .bashrc)

.. code-block::

   export PATH=$HOME/.local/bin:$PATH

Restart your shell to apply the changes.

To install ``amber``:

.. code-block::

   git clone https://github.com/GOATS2K/amber.git
   cd amber
   pip3 install . --user

Run ``amber config`` to edit your config.


**Troubleshooting**

If your ``pip`` install fails with:

.. code-block::

   Directory '.' is not installable. File 'setup.py' not found.

or

.. code-block::

   Installing build dependencies ... done
    Complete output from command python setup.py egg_info:
    Traceback (most recent call last):
      File "<string>", line 1, in <module>
      File "/usr/lib/python3.7/tokenize.py", line 447, in open
        buffer = _builtin_open(filename, 'rb')
    FileNotFoundError: [Errno 2] No such file or directory: '/tmp/pip-req-build-r9ap2n3a/setup.py'


Your version of ``pip`` is too old and needs to be upgraded.

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
