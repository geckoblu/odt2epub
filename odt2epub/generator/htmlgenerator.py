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
from odt2epub.contenthandler import Header, List


class HTMLGenerator:

    def __init__(self, document, keep_css_class=True, export_css=False, inline_css=False, insert_sigil_toc_id=True, insert_split_marker=False, verbose=0):
        self.document = document
        self.keep_css_class = keep_css_class
        self.export_css = export_css
        self.inline_css = inline_css
        self.insert_sigil_toc_id = insert_sigil_toc_id
        self.insert_split_marker = insert_split_marker
        self.verbose = verbose

        self.cssclassToExport = []
        self.sigil_toc_id_counter = 0
        # self.lastParagraphClass = None

    def getHTML(self, cssrelfilename):
        htmltxt = HTML_HEAD % f'<link href="{cssrelfilename}" rel="stylesheet" type="text/css" />'

        htmltxt += self.paragraphsToStr(self.document.paragraps)

        htmltxt += HTML_TAIL

        return htmltxt

    def write(self, htmlfilename):
        if self.verbose > 0:
            print(_gt('Output: %s') % htmlfilename)

        if self.export_css:
            fname, __ = os.path.splitext(htmlfilename)
            cssfilename = '%s.css' % fname
            cssrelfilename = f'./{os.path.split(fname)[1]}.css'
        else:
            cssrelfilename = '../Styles/Style0001.css'

        htmltxt = self.getHTML(cssrelfilename)

        with open(htmlfilename, 'w', encoding='utf-8') as fout:
            fout.write(htmltxt)

        # print(sorted(set(self.cssclassToExport)))

        if self.export_css:
            self.writeCss(cssfilename)

    def writeCss(self, cssfilename):

        self.cssclassToExport = sorted(set(self.cssclassToExport))

        csstxt = ''

        # Headers Style
        for cssclass in self.cssclassToExport:
            if cssclass.startswith('Heading'):
                style = self.document.getStyleByDisplayName(cssclass)
                csstxt += f'h{style.getHeaderLevel()} {{\n'
                csstxt += self.getCSStyleProperties(style)
                csstxt += '}\n\n'

        # P Style
        style = self.document.getStyleByDisplayName('Text body')
        csstxt += 'p {\n'
        csstxt += '\tmargin: 0 0 0 0;\n'
        csstxt += self.getCSStyleProperties(style)
        csstxt += '}\n\n'

        # Others Style
        for cssclass in self.cssclassToExport:
            if not cssclass.startswith('Heading') and cssclass != 'Text body':
                style = self.document.getStyleByDisplayName(cssclass)
                csstxt += f'.{cssclass.lower()} {{\n'
                csstxt += self.getCSStyleProperties(style)
                csstxt += '}\n\n'

        with open(cssfilename, 'w', encoding='utf-8') as fout:
            fout.write(csstxt)

    def getCSStyleProperties(self, style):
        csstxt = ''

        alignment = style.getAlignment()
        if alignment:
            csstxt += f'\ttext-align: {alignment};\n'

        fontStyle = style.getFontStyle()
        if fontStyle:
            csstxt += f'\tfont-style: {fontStyle};\n'

        fontWeight = style.getFontWeight()
        if fontWeight:
            csstxt += f'\tfont-weight: {fontWeight};\n'

        return csstxt

    def paragraphsToStr(self, paragraps):
        htmltxt = ''

        for paragraph in paragraps:
            if isinstance(paragraph, Header):
                line = self.headerToStr(paragraph)
            elif isinstance(paragraph, List):
                line = self.listToStr(paragraph)
            else:
                line = self.paragraphToStr(paragraph)
            # print(line)
            htmltxt += '%s\n' % line

        return htmltxt

    def listToStr(self, list_):
        if list_.list_style == 'number':
            htmltxt = '<ol>\n'
        else:
            htmltxt = '<ul>\n'

        for listitem in list_.items:
            htmltxt += '<li>\n' + self.paragraphsToStr(listitem.paragraps) + '</li>\n'

        if list_.list_style == 'number':
            htmltxt += '</ol>\n'
        else:
            htmltxt += '</ul>\n'

        return htmltxt

    def headerToStr(self, header):

        cssclass = header.getStyleDisplayName()
        self.cssclassToExport.append(cssclass)

        if self.insert_sigil_toc_id:
            s = f'<h{header.getLevel()} id="sigil_toc_id_{self.sigil_toc_id_counter}">'
            self.sigil_toc_id_counter += 1
        else:
            s = f'<h{header.getLevel()}>'
        s += self.contentToStr(header.content)
        s += f'</h{header.getLevel()}>'
        return s

    def paragraphToStr(self, paragraph):
        cssclass = paragraph.getStyleDisplayName()

        # if cssclass == 'Quotations':
        #     print(cssclass, self.lastParagraphClass)

        if self.keep_css_class and cssclass != 'Text body':
            # style = self.document.styles[cssclass]
            # if 'loext:contextual-spacing' in style.properties and style.properties['loext:contextual-spacing'].upper() == 'TRUE':
            #     print(cssclass, self.lastParagraphClass)
            s = f'<p class="{cssclass.lower()}">'
            self.cssclassToExport.append(cssclass)
        else:
            s = '<p>'
        s += self.contentToStr(paragraph.content)
        s += f'</p>'

        # self.lastParagraphClass = cssclass

        return s

    def contentToStr(self, content):
        s = ''
        for text, style in content:
            if style:
                if style.isItalic(self.keep_css_class):
                    s += '<i>'
                if style.isBold():
                    s += '<b>'

            s += text

            if style:
                if style.isBold():
                    s += '</b>'
                if style.isItalic(self.keep_css_class):
                    s += '</i>'
        return s

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
