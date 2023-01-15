import ast
import logging
import mimetypes
import os
import re
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path

from convert_to_txt import __version__

# import ipdb

logger = logging.getLogger('convert_lib')
logger.setLevel(logging.CRITICAL + 1)


# =====================
# Default config values
# =====================

# convert_to_txt options
# ======================
CONVERT_PAGES = None
DJVU_CONVERT_METHOD = 'djvutxt'
EPUB_CONVERT_METHOD = 'epubtxt'
MSWORD_CONVERT_METHOD = 'textutil'
PDF_CONVERT_METHOD = 'pdftotext'

# Logging options
# ===============
LOGGING_FORMATTER = 'only_msg'
LOGGING_LEVEL = 'info'


class Result:
    def __init__(self, stdout='', stderr='', returncode=None, args=None):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
        self.args = args

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'stdout={str(self.stdout).strip()}, ' \
               f'stderr={str(self.stderr).strip()}, ' \
               f'returncode={self.returncode}, args={self.args}'


# ------
# Colors
# ------
COLORS = {
    'GREEN': '\033[0;36m',  # 32
    'RED': '\033[0;31m',
    'YELLOW': '\033[0;33m',  # 32
    'BLUE': '\033[0;34m',  #
    'VIOLET': '\033[0;35m',  #
    'BOLD': '\033[1m',
    'NC': '\033[0m',
}
_COLOR_TO_CODE = {
    'g': COLORS['GREEN'],
    'r': COLORS['RED'],
    'y': COLORS['YELLOW'],
    'b': COLORS['BLUE'],
    'v': COLORS['VIOLET'],
    'bold': COLORS['BOLD']
}


def color(msg, msg_color='y', bold_msg=False):
    msg_color = msg_color.lower()
    colors = list(_COLOR_TO_CODE.keys())
    assert msg_color in colors, f'Wrong color: {msg_color}. Only these ' \
                                f'colors are supported: {msg_color}'
    msg = bold(msg) if bold_msg else msg
    msg = msg.replace(COLORS['NC'], COLORS['NC']+_COLOR_TO_CODE[msg_color])
    return f"{_COLOR_TO_CODE[msg_color]}{msg}{COLORS['NC']}"


def blue(msg):
    return color(msg, 'b')


def bold(msg):
    return color(msg, 'bold')


def green(msg):
    return color(msg, 'g')


def red(msg):
    return color(msg, 'r')


def violet(msg):
    return color(msg, 'v')


def yellow(msg):
    return color(msg)


def catdoc(input_file, output_file):
    cmd = f'catdoc "{input_file}"'
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Everything on the stdout must be copied to the output file
    if result.returncode == 0:
        with open(output_file, 'w') as f:
            f.write(result.stdout)
    return convert_result_from_shell_cmd(result)


# Ref.: https://stackoverflow.com/a/28909933
def command_exists(cmd):
    return shutil.which(cmd) is not None


def convert_result_from_shell_cmd(old_result):
    new_result = Result()

    for attr_name, new_val in new_result.__dict__.items():
        old_val = getattr(old_result, attr_name)
        if old_val is None:
            shell_args = getattr(old_result, 'args', None)
            # logger.debug(f'result.{attr_name} is None. Shell args: {shell_args}')
        else:
            if isinstance(new_val, str):
                try:
                    new_val = old_val.decode('UTF-8')
                except (AttributeError, UnicodeDecodeError) as e:
                    if type(e) == UnicodeDecodeError:
                        # old_val = b'...'
                        new_val = old_val.decode('unicode_escape')
                    else:
                        # `old_val` already a string
                        # logger.debug('Error decoding old value: {}'.format(old_val))
                        # logger.debug(e.__repr__())
                        # logger.debug('Value already a string. No decoding necessary')
                        new_val = old_val
                try:
                    new_val = ast.literal_eval(new_val)
                except (SyntaxError, ValueError) as e:
                    # NOTE: ValueError might happen if value consists of [A-Za-z]
                    # logger.debug('Error evaluating the value: {}'.format(old_val))
                    # logger.debug(e.__repr__())
                    # logger.debug('Aborting evaluation of string. Will consider
                    # the string as it is')
                    pass
            else:
                new_val = old_val
        setattr(new_result, attr_name, new_val)
    return new_result


def convert(input_file, output_file=None,
            convert_pages=CONVERT_PAGES,
            djvu_convert_method=DJVU_CONVERT_METHOD,
            epub_convert_method=EPUB_CONVERT_METHOD,
            msword_convert_method=MSWORD_CONVERT_METHOD,
            pdf_convert_method=PDF_CONVERT_METHOD,
            **kwargs):
    func_params = locals().copy()
    file_hash = None
    mime_type = get_mime_type(input_file)
    logger.debug(f'mime type: {mime_type}')
    if mime_type == 'text/plain':
        logger.warning(yellow('The file is already in .txt'))
        # Return text if no output file was specified
        if output_file is None:
            with open(input_file, 'r') as f:
                text = f.read()
            return text
        else:
            return 0
    return_txt = False
    # Create temp output file if output file not specified by user
    if output_file is None:
        return_txt = True
        output_file = tempfile.mkstemp(suffix='.txt')[1]
    else:
        output_file = Path(output_file)
        # Check first that the output text file is valid
        if output_file.suffix != '.txt':
            logger.error(red("The output file needs to have a .txt extension!"))
            return 1
        # Create output file text if it doesn't exist
        if output_file.exists():
            logger.warning(f"{yellow('Output text file already exists:')} {output_file.name}")
            logger.debug(f"Full path of output text file: '{output_file.absolute()}'")
        else:
            # Create output text file
            touch(output_file)
    func_params['mime_type'] = mime_type
    func_params['output_file'] = output_file
    logger.info("Starting document conversion to txt...")
    result = convert_to_txt(**func_params)
    statuscode = result.returncode
    if statuscode == 0:
        logger.debug('Conversion terminated')
    # Check conversion
    logger.debug('Checking converted text...')
    if statuscode == 0 and isalnum_in_file(output_file):
        logger.debug("Converted text is valid!")
    else:
        logger.error(red("Conversion failed!"))
        size = os.stat(output_file).st_size
        if size == 0:
            logger.error(red('The converted file is empty'))
        else:
            logger.error(red(f'The converted txt with size {os.stat(output_file).st_size} '
                             'bytes does not seem to contain text'))
        # Only remove output file if it is a temp file (i.e. return_txt = True)
        if return_txt:
            remove_file(output_file)
        return 1
    logger.info(blue("Conversion successful!"))
    # Only remove output file if it is a temp file (i.e. return_txt = True)
    if return_txt:
        with open(output_file, 'r', encoding="utf8", errors='ignore') as f:
            text = f.read()
        assert text
        remove_file(output_file)
        return text
    else:
        return 0


# Tries to convert the supplied ebook file into .txt. It uses calibre's
# ebook-convert tool. For optimization, if present, it will use pdftotext
# for pdfs, catdoc for word files and djvutxt for djvu files.
# Ref.: https://bit.ly/2HXdf2I
def convert_to_txt(input_file, output_file, mime_type,
                   convert_pages=CONVERT_PAGES,
                   djvu_convert_method=DJVU_CONVERT_METHOD,
                   epub_convert_method=EPUB_CONVERT_METHOD,
                   msword_convert_method=MSWORD_CONVERT_METHOD,
                   pdf_convert_method=PDF_CONVERT_METHOD, **kwargs):
    if mime_type.startswith('image/vnd.djvu') \
         and djvu_convert_method == 'djvutxt' and command_exists('djvutxt'):
        logger.debug('The file looks like a djvu, using djvutxt to extract the text')
        result = djvutxt(input_file, output_file, pages=convert_pages)
    elif mime_type.startswith('application/epub+zip') \
            and epub_convert_method == 'epubtxt' and command_exists('unzip'):
        logger.debug('The file looks like an epub, using epubtxt to extract the text')
        result = epubtxt(input_file, output_file)
    elif mime_type == 'application/msword' \
            and msword_convert_method in ['catdoc', 'textutil'] \
            and (command_exists('catdoc') or command_exists('textutil')):
        msg = 'The file looks like a doc, using {} to extract the text'
        if command_exists('catdoc'):
            logger.debug(msg.format('catdoc'))
            result = catdoc(input_file, output_file)
        else:
            logger.debug(msg.format('textutil'))
            result = textutil(input_file, output_file)
    elif mime_type == 'application/pdf' and pdf_convert_method == 'pdftotext' \
            and command_exists('pdftotext'):
        logger.debug('The file looks like a pdf, using pdftotext to extract the text')
        if convert_pages:
            text = ''
            logger.debug(f'These are all the pages that need to be converted: {convert_pages}')
            for p in convert_pages.split(','):
                if '-' in p:
                    p1, p2 = p.split('-')
                    p1 = int(p1)
                    p2 = int(p2)
                    if p1 > p2:
                        pages_to_process = sorted(range(p2, p1 + 1), reverse=True)
                    else:
                        pages_to_process = sorted(range(p1, p2 + 1))
                else:
                    pages_to_process = [int(p)]
                logger.debug(f'Pages to process: {pages_to_process}')
                for i, page_to_process in enumerate(pages_to_process, start=1):
                    logger.debug(f'Processing page {i} of {len(pages_to_process)}')
                    logger.debug(f'Page number: {page_to_process}')
                    tmp_file_txt = tempfile.mkstemp(suffix='.txt')[1]
                    logger.debug(f'Using tmp file {tmp_file_txt}')
                    result = pdftotext(input_file, tmp_file_txt,
                                       first_page_to_convert=page_to_process,
                                       last_page_to_convert=page_to_process)
                    if result.returncode == 0:
                        logger.debug(f"Result of 'pdftotext':\n{result}")
                        with open(tmp_file_txt, 'r') as f:
                            data = f.read()
                            # logger.debug(f"Text content of page {page_to_process}:\n{data}")
                        text += data
                    else:
                        msg = red(f"Document couldn't be converted to txt: {result}")
                        logger.error(f'{msg}')
                        logger.error(f'Skipping current page ({page_to_process})')
                    # Remove temporary file
                    logger.debug('Cleaning up tmp file')
                    remove_file(tmp_file_txt)
            logger.debug('Saving the text content')
            with open(output_file, 'w') as f:
                f.write(text)
            return convert_result_from_shell_cmd(Result(returncode=0))
        else:
            logger.debug('All pages from the pdf document will be converted to txt')
            result = pdftotext(input_file, output_file)
    elif (not mime_type.startswith('image/vnd.djvu')) \
            and mime_type.startswith('image/'):
        msg = f'The file looks like a normal image ({mime_type}), skipping ' \
              'ebook-convert usage!'
        logger.debug(msg)
        return convert_result_from_shell_cmd(Result(stderr=msg, returncode=1))
    else:
        logger.debug(f"Trying to use calibre's ebook-convert to convert the {mime_type} file to .txt")
        result = ebook_convert(input_file, output_file)
    logger.debug(f'Result from conversion: {result}')
    return result


def djvutxt(input_file, output_file, pages=None):
    pages = f'--page={pages}' if pages else ''
    cmd = f'djvutxt "{input_file}" "{output_file}" {pages}'
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


def ebook_convert(input_file, output_file):
    cmd = f'ebook-convert "{input_file}" "{output_file}"'
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


def epubtxt(input_file, output_file):
    cmd = f'unzip -c "{input_file}"'
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if not result.stderr:
        text = str(result.stdout)
        with open(output_file, 'w') as f:
            f.write(text)
        result.stdout = text
    return convert_result_from_shell_cmd(result)


# Using Python built-in module mimetypes
def get_mime_type(file_path):
    return mimetypes.guess_type(file_path)[0]


def isalnum_in_file(file_path):
    with open(file_path, 'r', encoding="utf8", errors='ignore') as f:
        isalnum = False
        for line in f:
            for ch in line:
                if ch.isalnum():
                    isalnum = True
                    break
            if isalnum:
                break
    return isalnum


def pdftotext(input_file, output_file, first_page_to_convert=None, last_page_to_convert=None):
    first_page = f'-f {first_page_to_convert}' if first_page_to_convert else ''
    last_page = f'-l {last_page_to_convert}' if last_page_to_convert else ''
    pages = f'{first_page} {last_page}'.strip()
    cmd = f'pdftotext "{input_file}" "{output_file}" {pages}'
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


def remove_file(file_path):
    # Ref.: https://stackoverflow.com/a/42641792
    try:
        os.remove(file_path)
        return 0
    except OSError as e:
        logger.error(red(f'{e.filename} - {e.strerror}.'))
        return 1


def setup_log(quiet=False, verbose=False, logging_level=LOGGING_LEVEL,
              logging_formatter=LOGGING_FORMATTER):
    if not quiet:
        for logger_name in ['convert_script', 'convert_lib']:
            logger_ = logging.getLogger(logger_name)
            if verbose:
                logger_.setLevel('DEBUG')
            else:
                logging_level = logging_level.upper()
                logger_.setLevel(logging_level)
            # Create console handler and set level
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            # Create formatter
            if logging_formatter:
                formatters = {
                    'console': '%(name)-10s | %(levelname)-8s | %(message)s',
                    # 'console': '%(asctime)s | %(levelname)-8s | %(message)s',
                    'only_msg': '%(message)s',
                    'simple': '%(levelname)-8s %(message)s',
                    'verbose': '%(asctime)s | %(name)-10s | %(levelname)-8s | %(message)s'
                }
                formatter = logging.Formatter(formatters[logging_formatter])
                # Add formatter to ch
                ch.setFormatter(formatter)
            # Add ch to logger
            logger_.addHandler(ch)
        # =============
        # Start logging
        # =============
        logger.debug("Running {} v{}".format(__file__, __version__))
        logger.debug("Verbose option {}".format("enabled" if verbose else "disabled"))


# macOS equivalent for catdoc
# See https://stackoverflow.com/a/44003923/14664104
def textutil(input_file, output_file):
    cmd = f'textutil -convert txt "{input_file}" -output "{output_file}"'
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


def touch(path, mode=0o666, exist_ok=True):
    logger.debug(f"Creating file: '{path}'")
    Path(path).touch(mode, exist_ok)
    logger.debug("File created!")
