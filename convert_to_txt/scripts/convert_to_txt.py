"""
The script convert_to_txt.py converts documents (pdf, djvu, epub, word) to txt. It is based on the great ebook-tools 
which is written in Shell by na--.

Ref.: https://github.com/na--/ebook-tools
"""
import argparse
import logging
import os

from convert_to_txt import __version__
from convert_to_txt.lib import (convert, setup_log, blue, green, red, yellow,
                 LOGGING_FORMATTER, LOGGING_LEVEL, CONVERT_PAGES,
                 DJVU_CONVERT_METHOD, EPUB_CONVERT_METHOD, MSWORD_CONVERT_METHOD,
                 PDF_CONVERT_METHOD)

# import ipdb

logger = logging.getLogger('convert_script')

# =====================
# Default config values
# =====================

# Misc options
# ============
QUIET = False
OUTPUT_FILE = 'output.txt'


class ArgumentParser(argparse.ArgumentParser):

    def error(self, message):
        print_(self.format_usage().splitlines()[0])
        self.exit(2, red(f'\nerror: {message}\n'))


class MyFormatter(argparse.HelpFormatter):
    """
    Corrected _max_action_length for the indenting of subactions
    """

    def add_argument(self, action):
        if action.help is not argparse.SUPPRESS:

            # find all invocations
            get_invocation = self._format_action_invocation
            invocations = [get_invocation(action)]
            current_indent = self._current_indent
            for subaction in self._iter_indented_subactions(action):
                # compensate for the indent that will be added
                indent_chg = self._current_indent - current_indent
                added_indent = 'x' * indent_chg
                invocations.append(added_indent + get_invocation(subaction))
            # print_('inv', invocations)

            # update the maximum item length
            invocation_length = max([len(s) for s in invocations])
            action_length = invocation_length + self._current_indent
            self._action_max_length = max(self._action_max_length,
                                          action_length)

            # add the item to the list
            self._add_item(self._format_action, [action])

    # Ref.: https://stackoverflow.com/a/23941599/14664104
    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            parts = []
            # if the Optional doesn't take a value, format is:
            #    -s, --long
            if action.nargs == 0:
                parts.extend(action.option_strings)

            # if the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            # change to
            #    -s, --long ARGS
            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    # parts.append('%s %s' % (option_string, args_string))
                    parts.append('%s' % option_string)
                parts[-1] += ' %s'%args_string
            return ', '.join(parts)


class OptionsChecker:
    def __init__(self, add_opts, remove_opts):
        self.add_opts = init_list(add_opts)
        self.remove_opts = init_list(remove_opts)

    def check(self, opt_name):
        return not self.remove_opts.count(opt_name) or \
               self.add_opts.count(opt_name)


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


# General options
def add_general_options(parser, add_opts=None, remove_opts=None,
                        program_version=__version__,
                        title='General options'):
    checker = OptionsChecker(add_opts, remove_opts)
    parser_general_group = parser.add_argument_group(title=title)
    if checker.check('help'):
        parser_general_group.add_argument('-h', '--help', action='help',
                                          help='Show this help message and exit.')
    if checker.check('version'):
        parser_general_group.add_argument(
            '-v', '--version', action='version',
            version=f'%(prog)s v{program_version}',
            help="Show program's version number and exit.")
    if checker.check('quiet'):
        parser_general_group.add_argument(
            '-q', '--quiet', action='store_true',
            help='Enable quiet mode, i.e. nothing will be printed.')
    if checker.check('verbose'):
        parser_general_group.add_argument(
            '--verbose', action='store_true',
            help='Print various debugging information, e.g. print traceback '
                 'when there is an exception.')
    if checker.check('log-level'):
        parser_general_group.add_argument(
            '--log-level', dest='logging_level',
            choices=['debug', 'info', 'warning', 'error'], default=LOGGING_LEVEL,
            help='Set logging level.' + get_default_message(LOGGING_LEVEL))
    if checker.check('log-format'):
        parser_general_group.add_argument(
            '--log-format', dest='logging_formatter',
            choices=['console', 'only_msg', 'simple',], default=LOGGING_FORMATTER,
            help='Set logging formatter.' + get_default_message(LOGGING_FORMATTER))
    return parser_general_group


def get_default_message(default_value):
    return green(f' (default: {default_value})')


def init_list(list_):
    return [] if list_ is None else list_


def print_(msg):
    global QUIET
    if not QUIET:
        print(msg)


# Ref.: https://stackoverflow.com/a/4195302/14664104
def required_length(nmin, nmax, is_list=True):
    class RequiredLength(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if isinstance(values, str):
                tmp_values = [values]
            else:
                tmp_values = values
            if not nmin <= len(tmp_values) <= nmax:
                if nmin == nmax:
                    msg = 'argument "{f}" requires {nmin} arguments'.format(
                        f=self.dest, nmin=nmin, nmax=nmax)
                else:
                    msg = 'argument "{f}" requires between {nmin} and {nmax} ' \
                          'arguments'.format(f=self.dest, nmin=nmin, nmax=nmax)
                raise argparse.ArgumentTypeError(msg)
            setattr(args, self.dest, values)
    return RequiredLength


def setup_argparser():
    width = os.get_terminal_size().columns - 5
    name_input = 'input_file'
    name_output = 'output_file'
    usage_msg = blue(f'%(prog)s [OPTIONS] {{{name_input}}} [{{{name_output}}}]')
    desc_msg = 'Convert documents (pdf, djvu, epub, word) to txt.'
    parser = ArgumentParser(
        description="",
        usage=f"{usage_msg}\n\n{desc_msg}",
        add_help=False,
        formatter_class=lambda prog: MyFormatter(
            prog, max_help_position=50, width=width))
    general_group = add_general_options(
        parser,
        remove_opts=[],
        program_version=__version__,
        title=yellow('General options'))
    # ======================
    # Convert-to-txt options
    # ======================
    convert_group = parser.add_argument_group(title=yellow('Convert-to-txt options'))
    convert_group.add_argument(
        '-p', '--pages', dest='pages', metavar='PAGES', default=CONVERT_PAGES,
        help=""""Specify which pages should be processed. When this option is
            not specified, the text of all pages of the documents is concatenated
            into the output file. The page specification PAGES contains one or more
            comma-separated page ranges. A page range is either a page number, or
            two page numbers separated by a dash. For instance, specification 1-10
            outputs pages 1 to 10, and specification 1,3,99999-4 outputs pages 1
            and 3, followed by all the document pages in reverse order up to page
            4." Ref.: https://man.archlinux.org/man/djvutxt.1.en""")
    convert_group.add_argument(
        '--djvu', dest='djvu_convert_method',
        choices=['djvutxt', 'ebook-convert'], default=DJVU_CONVERT_METHOD,
        help='Set the conversion method for djvu documents.'
             + get_default_message(DJVU_CONVERT_METHOD))
    convert_group.add_argument(
        '--epub', dest='epub_convert_method',
        choices=['epubtxt', 'ebook-convert'], default=EPUB_CONVERT_METHOD,
        help='Set the conversion method for epub documents.'
             + get_default_message(EPUB_CONVERT_METHOD))
    convert_group.add_argument(
        '--msword', dest='msword_convert_method',
        choices=['textutil', 'catdoc', 'ebook-convert'],
        default=MSWORD_CONVERT_METHOD,
        help='Set the conversion method for msword documents.'
             + get_default_message(MSWORD_CONVERT_METHOD))
    convert_group.add_argument(
        '--pdf', dest='pdf_convert_method',
        choices=['pdftotext', 'ebook-convert'], default=PDF_CONVERT_METHOD,
        help='Set the conversion method for pdf documents.'
             + get_default_message(PDF_CONVERT_METHOD))
    # ==================
    # Input/output files
    # ==================
    input_output_files_group = parser.add_argument_group(
        title=yellow('Input/Output files'))
    input_output_files_group.add_argument(
        'input',
        help='Path of the file (pdf, djvu, epub, word) that will be converted to txt.')
    input_output_files_group.add_argument(
        'output', default=OUTPUT_FILE, nargs='*', action=required_length(0, 1),
        help='Path of the output txt file.'
             + get_default_message(OUTPUT_FILE))
    return parser


def show_exit_code(exit_code):
    msg = f'Program exited with {exit_code}'
    if exit_code == 1:
        logger.error(red(f'{msg}'))
    else:
        logger.debug(msg)


def main():
    global QUIET
    try:
        parser = setup_argparser()
        args = parser.parse_args()
        QUIET = args.quiet
        setup_log(args.quiet, args.verbose, args.logging_level, args.logging_formatter)
        # Actions
        if isinstance(args.output, list):
            output = args.output[0]
        else:
            output = args.output
        exit_code = convert(args.input, output, convert_pages=args.pages,
            djvu_convert_method=args.djvu_convert_method,
            epub_convert_method=args.epub_convert_method,
            msword_convert_method=args.msword_convert_method,
            pdf_convert_method=args.pdf_convert_method)
    except KeyboardInterrupt:
        print_(yellow('\nProgram stopped!'))
        exit_code = 2
    except Exception as e:
        print_(yellow('Program interrupted!'))
        logger.exception(e)
        exit_code = 1
    if __name__ != '__main__':
        show_exit_code(exit_code)
    return exit_code


if __name__ == '__main__':
    retcode = main()
    show_exit_code(retcode)
