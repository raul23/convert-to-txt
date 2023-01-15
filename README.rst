================================================
Convert documents (pdf, djvu, epub, word) to txt
================================================
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
