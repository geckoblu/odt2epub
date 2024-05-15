'''
This file is part of odt2epub.

odt2epub is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

odt2epub is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with odt2epub.  If not, see <http://www.gnu.org/licenses/>.

Copyright (C) 2015 Alessio Piccoli <alepic@geckoblu.net>
'''
from argparse import ArgumentParser, Action, SUPPRESS, ArgumentTypeError
from argparse import FileType
from argparse import RawDescriptionHelpFormatter
import os
import sys
import shutil

try:
    from gettext import gettext as _gt, ngettext
except ImportError:

    def _gt(message):
        return message

    def ngettext(singular, plural, n):
        if n == 1:
            return singular
        else:
            return plural

from odt2epub.odtparser import OdtParser
from odt2epub.txtparser import TxtParser
from odt2epub.generator.htmlgenerator import HTMLGenerator
from odt2epub.generator.epubwriter import EpubWriter

__all__ = []
__version__ = 0.1
__date__ = '2015-09-11'
__updated__ = '2015-09-11'

# DEBUG = 1
# TESTRUN = 0
# PROFILE = 0


class _LicenseAction(Action):

    def __init__(self,
                 option_strings,
                 version=None,
                 dest=SUPPRESS,
                 default=SUPPRESS,
                 _help="show program's license and exit"):
        super(_LicenseAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=_help)
        self.version = version

    def __call__(self, parser, namespace, values, option_string=None):
        _license = '''odt2epub is an odt to epub converter.

    Copyright (C) 2015 Alessio Piccoli <alepic@geckoblu.net>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.'''
        formatter = parser._get_formatter()
        formatter.add_text(_license)
        parser._print_message(formatter.format_help(), sys.stdout)
        parser.exit()


def filetype(path, mode='r'):
    filename = os.path.expanduser(path)
    filename = os.path.abspath(filename)
    f = None
    try:
        f = open(filename, mode)
    except Exception as e:
        message = _gt("can't open '%s': %s")
        raise ArgumentTypeError(message % (path, e))
    finally:
        if f:
            f.close()
    __, ext = os.path.splitext(filename)
    if ext.lower() != '.odt' and ext.lower() != '.txt':
        message = _gt("not an odt nor a txt file '%s'")
        raise ArgumentTypeError(message % path)

    return filename


def parse_cmdline(argv=None):
    '''Parse command line options'''
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = _gt('odt2epub is an odt to epub converter.')

    # Setup argument parser
    parser = ArgumentParser(prog='odt2epub', description=program_shortdesc, formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument(dest="odtfilename", help=_gt("odt file to convert"), metavar="<odt filename>", type=filetype)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', dest='verbose', action='count', help=_gt('set verbosity level [default: %(default)s]'), default=1)
    group.add_argument('-q', '--quiet', action='store_true', help=_gt('suppress non-error messages'))
    parser.add_argument('--output', choices=['epub', 'html'], type=str.lower, help='output\'s format [default: %(default)s]', default='epub')
    # parser.add_argument('--input', choices=['odt', 'txt'], type=str.lower, help='input\'s format [default: %(default)s]', default='odt')
    # parser.add_argument('--inline-css', action='store_true', help=_gt('inline generated css'))
    # parser.add_argument('--keep-css-class', action='store_true', help=_gt('keep css class'))
    # parser.add_argument('--export-css', action='store_true', help=_gt('export css'))
    # parser.add_argument('--insert-sigil-toc-id', action='store_true', help=_gt('insert Sigil toc id'))
    # parser.add_argument('--insert-split-marker', action='store_true', help=_gt('insert Sigil split marker before headers'))
    parser.add_argument('-V', '--version', action='version', version=program_version_message)
    parser.add_argument('-l', '--license', action=_LicenseAction)

    # Process arguments
    return parser.parse_args()


def main(argv=None):

    args = parse_cmdline(argv)

    if args.quiet:
        args.verbose = 0

    __, ext = os.path.splitext(args.odtfilename)

    if ext == '.odt':
        parser = OdtParser()
        document = parser.parse(args.odtfilename, args.verbose)
    elif ext == '.txt':
        parser = TxtParser()
        document = parser.parse(args.odtfilename, args.verbose)
    else:
        raise Exception(f"Unhandled input format '{ext}'")

    if args.output == 'html':
        fname, __ = os.path.splitext(args.odtfilename)
        htmlfilename = '%s.html' % fname

        generator = HTMLGenerator(document, flat_html=True, verbose=args.verbose)
        generator.write(htmlfilename)
    elif args.output == 'epub':
        fname, __ = os.path.splitext(args.odtfilename)
        epubfilename = '%s.epub' % fname

        writer = EpubWriter(document, verbose=args.verbose)
        writer.write(epubfilename)
        # shutil.copy(epubfilename, '%s.zip' % fname)
    else:
        raise Exception(f"Unhandled output format '{args.format}'")
