================================================
Convert documents (pdf, djvu, epub, word) to txt
================================================
The script `convert_to_txt.py <./convert_to_txt/scripts/convert_to_txt.py>`_ converts documents (pdf, djvu, epub, word) to txt.
It is based on the great `ebook-tools <https://github.com/na--/ebook-tools>`_ which is written in Shell by 
`na-- <https://github.com/na-->`_.

.. contents:: **Contents**
   :depth: 3
   :local:
   :backlinks: top

Dependencies
============
This is the environment on which the script `convert_to_txt.py <./convert_to_txt/scripts/convert_to_txt.py>`_ was tested:

* **Platform:** macOS
* **Python**: version **3.7**
* `textutil <https://ss64.com/osx/textutil.html>`_ or `catdoc <http://www.wagner.pp.ru/~vitus/software/catdoc/>`_: for converting *doc* to *txt*

  **NOTE:** On macOS, you don't need ``catdoc`` since it has the built-in ``textutil``
  command-line tool that converts any *txt*, *html*, *rtf*, 
  *rtfd*, *doc*, *docx*, *wordml*, *odt*, or *webarchive* file
* `DjVuLibre <http://djvu.sourceforge.net/>`_: it includes ``djvutxt`` for 
  converting *djvu* to *txt*
* `poppler <https://poppler.freedesktop.org/>`_: it includes ``pdftotext`` for converting *pdf* to *txt*

`:information_source:` *epub* is converted to *txt* by using ``unzip -c {input_file}``

**Optionally:**

- `calibre <https://calibre-ebook.com/>`_: for converting {*pdf*, *djvu*, *epub*, *msword*} to *txt* by using calibre's own 
  `ebook-convert <https://manual.calibre-ebook.com/generated/en/ebook-convert.html>`_
  
  `:warning:` ``ebook-convert`` is slower than the other conversion tools (``textutil``, ``catdoc``, ``pdftotext``, ``djvutxt``)

Installation
============
To install the `convert_to_txt <./convert_to_txt/>`_ package::

 $ pip install git+https://github.com/raul23/convert-to-txt#egg=convert-to-txt
 
**Test installation**

1. Test your installation by importing ``convert_to_txt`` and printing its
   version::

   $ python -c "import convert_to_txt; print(convert_to_txt.__version__)"

2. You can also test that you have access to the ``convert_to_txt.py`` script by
   showing the program's version::

   $ convert_to_txt --version

Uninstall
=========
To uninstall the `convert_to_txt <./convert_to_txt/>`_ package::

 $ pip uninstall convert_to_txt

Script options
==============
To display the script `convert_to_txt.py <./convert_to_txt/scripts/convert_to_txt.py>`_ list of options and their descriptions::

   $ convert_to_txt -h
   usage: convert_to_txt [OPTIONS] {input_file} [{output_file}]

   Convert documents (pdf, djvu, epub, word) to txt.

   General options:
     -h, --help                                Show this help message and exit.
     -v, --version                             Show program's version number and exit.
     -q, --quiet                               Enable quiet mode, i.e. nothing will be printed.
     --verbose                                 Print various debugging information, e.g. print traceback when there is an exception.
     --log-level {debug,info,warning,error}    Set logging level. (default: info)
     --log-format {console,only_msg,simple}    Set logging formatter. (default: only_msg)

   Convert-to-txt options:
     -p, --pages PAGES                         "Specify which pages should be processed. When this option is not specified, 
                                               the text of all pages of the documents is concatenated into the output file. 
                                               The page specification PAGES contains one or more comma-separated page ranges. 
                                               A page range is either a page number, or two page numbers separated by a dash. 
                                               For instance, specification 1-10 outputs pages 1 to 10, and specification 
                                               1,3,99999-4 outputs pages 1 and 3, followed by all the document pages in reverse 
                                               order up to page 4." 
                                               Ref.: https://man.archlinux.org/man/djvutxt.1.en
     --djvu {djvutxt,ebook-convert}            Set the conversion method for djvu documents. (default: djvutxt)
     --epub {epubtxt,ebook-convert}            Set the conversion method for epub documents. (default: epubtxt)
     --msword {textutil,catdoc,ebook-convert}  Set the conversion method for msword documents. (default: textutil)
     --pdf {pdftotext,ebook-convert}           Set the conversion method for pdf documents. (default: pdftotext)

   Input/Output files:
     input                                     Path of the file (pdf, djvu, epub, word) that will be converted to txt.
     output                                    Path of the output txt file. (default: output.txt)

`:information_source:` Explaining some of the options/arguments

- The option ``-p, --pages`` is taken straight from `djvutxt <https://man.archlinux.org/man/djvutxt.1.en>`_ option ``--page=pagespec``.

  `:warning:` Things to watch out when using the ``-p`` option
  
  - If the option ``-p`` is not used, then by default all pages from the given document will be converted.
  - If the given document is not a *pdf* or *djvu* file, then the option ``-p`` will be ignored.
- ``input`` and ``output`` are positional arguments. Thus they must follow directly each other. ``output`` is not required since by
  default the output *txt* file will be saved as ``output.txt`` directly under the working directory.
  
  `:warning:` ``output`` needs to have a *.txt* extension!

How the conversion is applied
=============================
Here are the important steps that the script `convert_to_txt.py <./convert_to_txt/scripts/convert_to_txt.py>`_ 
follows when converting a given document to *txt*:

1. If the given document is already in *.txt*, then no need to go further!
2. According to the mime type, the corresponding conversion tool is called upon:

   i. *image/vnd.djvu*: ``djvutxt``
   ii. *application/epub+zip*: ``unzip``
   iii. *application/msword*: ``catdoc`` or ``textutil``
   iv. *application/pdf*: ``pdftotext``
   v. ``ebook-convert`` if the other conversion tools are not found
3. The output *txt* file is checked if it actually contains text. If it doesn't, the user is warned that OCR failed.

Files supported
===============
These are the files that are supported for conversion to *txt* and the corresponding conversion tools used:

+---------------------+------------------------------+------------------------------+------------------------------+
| Files supported     | Conversion tool #1           | Conversion tool #2           | Conversion tool #3           |
+=====================+==============================+==============================+==============================+
| *pdf*               | ``pdftotext``                | ``ebook-convert`` (calibre)  | -                            |
+---------------------+------------------------------+------------------------------+------------------------------+
| *djvu*              | ``djvutxt``                  | ``ebook-convert`` (calibre)  | -                            |
+---------------------+------------------------------+------------------------------+------------------------------+
| *epub*              | ``epubtxt``                  | ``ebook-convert`` (calibre)  | -                            |
+---------------------+------------------------------+------------------------------+------------------------------+
| *docx* (Word 2007)  | ``ebook-convert`` (calibre)  | -                            | -                            |
+---------------------+------------------------------+------------------------------+------------------------------+
| *doc* (Word 97)     | ``textutil`` (macOS)         | ``catdoc``                   | ``ebook-convert`` (calibre)  |
+---------------------+------------------------------+------------------------------+------------------------------+
| *rtf*               | ``ebook-convert`` (calibre)  | -                            | -                            |
+---------------------+------------------------------+------------------------------+------------------------------+

`:information_source:` Some explanations about the table

- ``epubtxt`` is a fancy way to say ``unzip``.
- By default, ``ebook-convert`` (calibre) is always used as a last resort since it is slower than
  the other conversion tools.

For comparison, here are the times taken to convert completely a 154-pages PDF document to *txt* for both supported conversion methods:

- ``pdftotext``: 4.27s
- ``ebook-convert`` (calibre): 80.91s 

Example: convert a ``pdf`` file to ``txt``
==========================================
Through the script ``convert_to_txt.py``
----------------------------------------
Let's say you want to convert specific pages of a *pdf* file to *txt*, then the following command will do the trick::

 convert_to_txt ~/Data/convert/K.pdf K.txt -p 15-10,3,23-30 

`:information_source:` Explaining the command

- ``-p 15-10,3,23-30``: specifies that pages 15 to 10 (reverse order), 3 and 23 to 30 from the given *pdf* document will be converted to *txt*.

  `:warning:` No spaces when specifying the pages.
- ``~/Data/convert/K.pdf K.txt``: these are the input and output files, respectively.

  **NOTE:** by default if no output file is specified, then the converted text will be saved as ``output.txt`` 
  directly under the working directory.

Sample output::

 Starting document conversion to txt...
 Conversion successful!

Through the API
---------------
To convert a *pdf* file to *txt* using the API:

.. code-block:: python

   from convert_to_txt.lib import convert
   
   txt = convert('/Users/test/Data/convert/B.pdf', convert_pages='10-12')
   # Do something with `txt`

`:information_source:` Explaining the snippet of code

- ``convert(input_file, output_file=None, convert_pages=CONVERT_PAGES)``:

  By default ``output_file`` is None and hence ``convert()`` will return the text from the conversion. 
  If you set ``output_file`` to for example **output.txt**, then ``convert()`` will just return a status code
  (1 for error and 0 for success) and will write the text from the conversion to **output.txt**.
- The variable ``txt`` will contain the text from the conversion.

By default when using the API, the loggers are disabled. If you want to enable them, use the
function ``setup_log()`` at the beginning of your code before the conversion:

.. code-block:: python

   from convert_pages.lib import convert, setup_log
   
   setup_log(logging_level='INFO')
   txt = convert('/Users/test/Data/convert/B.pdf', convert_pages='10-12')
   # Do something with `txt`
   
Sample output::

 Output text file already exists: output.txt
 Starting document conversion to txt...
 Conversion successful!

Finally, just like you can set the conversion method via the `command-line <#script-options>`_, you can also do it via the API: 

.. code-block:: python

   from convert_pages.lib import convert
   
   txt = convert('/Users/test/Data/convert/B.pdf', convert_pages='10-12', pdf_convert_method='ebook-convert')
   
`:information_source:` The full signature for the function ``convert()``:

.. code-block:: python

   convert(input_file, output_file=None,
           convert_pages=None,
           djvu_convert_method='djvutxt',
           epub_convert_method='epubtxt',
           msword_convert_method='textutil',
           pdf_convert_method='pdftotext', **kwargs)
 
