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
import os

from odt2epub import _gt
from odt2epub.generator.htmlparagraph import HTMLParagraph


class HTMLGenerator:

    def __init__(self, document, args):
        self.document = document
        self.keep_css_class = args.keep_css_class
        self.insert_split_marker = args.insert_split_marker

        self.verbose = args.verbose
        self.inline_css = args.inline_css

        fname, _ = os.path.splitext(args.odtfilename)
        self.htmlfilename = '%s.html' % fname

        if self.verbose > 0:
            print(_gt('Output: %s') % self.htmlfilename)

    def write(self):
        with open(self.htmlfilename, 'w', encoding='utf-8') as fout:

            fout.write(HTML_HEAD % self._get_css())

            for paragraph in self.document.paragraps:
                p = HTMLParagraph(paragraph, self.keep_css_class, self.insert_split_marker)
                fout.write('%s\n' % p)

            fout.write(HTML_TAIL)

    def _get_css(self):
        if self.inline_css:
            return INLINE_CSS
        else:
            return '<link href="../Styles/Style0001.css" rel="stylesheet" type="text/css" />'


HTML_HEAD = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title></title>
%s
<meta charset="UTF-8" />
</head>
<body>

"""

HTML_TAIL = """
</body>
</html>
"""

INLINE_CSS = """<style>
    body {
        text-align: justify;
    }

    p {
        margin: 0 0 0 0;
        text-indent: 0.5em;
    }

    .center {
        text-align: center;
    }

    .right {
        text-align: right;
    }
</style>
"""
