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
from odt2epub.generator.stylesheetgenerator import StylesheetGenerator


class HTMLGenerator:

    def __init__(self, document, keep_css_class=True, export_css=True, verbose=0):
        self.document = document
        self.verbose = verbose

        self.keep_css_class = keep_css_class
        self.export_css = export_css
        # self.inline_css = args.inline_css
        # self.insert_sigil_toc_id = args.insert_sigil_toc_id
        # self.insert_split_marker = args.insert_split_marker
        
        self._reset()

    def _reset(self):
        self.cssclassToExport = []
        self.noteToExport = []
        self.toc_id_counter = 0

    def get_html(self, cssrelfilename):
        self._reset()
        html = self.getHTML(cssrelfilename)

        stylesheetgenerator = StylesheetGenerator(self.document, self.cssclassToExport, self.verbose)
        csstxt = stylesheetgenerator.get_stylesheet()

        return ([html], csstxt)

    def getHTML(self, cssrelfilename):
        htmltxt = HTML_HEAD % f'<link href="{cssrelfilename}" rel="stylesheet" type="text/css" />'

        htmltxt += self.paragraphsToStr(self.document.paragraps)
        htmltxt += self.notesToStr()

        htmltxt += HTML_TAIL

        return htmltxt

    def write(self, htmlfilename):
        if self.verbose > 0:
            print(_gt('Output:  %s') % htmlfilename)

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

        stylesheetgenerator = StylesheetGenerator(self.document, self.cssclassToExport, self.verbose)
        csstxt = stylesheetgenerator.get_stylesheet()

        with open(cssfilename, 'w', encoding='utf-8') as fout:
            fout.write(csstxt)

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

        self.toc_id_counter += 1

        s = f'<h{header.getLevel()} id="hid_{self.toc_id_counter}">'
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
            selector = cssclass.lower().replace(' ', '_')
            s = f'<p class="{selector}">'
            self.cssclassToExport.append(cssclass)
        else:
            s = '<p>'
        s += self.contentToStr(paragraph.content)
        s += '</p>'
        if s == '<p></p>':
            s = '<p class="emptyline">&nbsp;</p>'

        # self.lastParagraphClass = cssclass

        return s

    def contentToStr(self, content):
        s = ''
        for typ, text, style in content:
            if typ == 'str':
                if style:  # Start style
                    if style.isItalic(self.keep_css_class):
                        s += '<i>'
                    if style.isBold():
                        s += '<b>'

                s += text

                if style:  # End style
                    if style.isBold():
                        s += '</b>'
                    if style.isItalic(self.keep_css_class):
                        s += '</i>'
            elif typ == 'note':
                note = text
                ref = note.id.replace('ftn', 'refn')
                s += f'<sup><a id="{ref}" href="#{note.id}">{note.citation}</a></sup>'
                self.noteToExport.append(note)
            elif typ == 'line-break':
                s += '<br/>'
            else:
                raise Exception(f'Unhandled content type: {typ}')
        return s

    def notesToStr(self):
        s = ''

        if len(self.noteToExport) > 0:
            s = '<div class="notes">\n'
            for note in self.noteToExport:
                ref = note.id.replace('ftn', 'refn')
                s += f'<p class="note"><a id="{note.id}" href="#{ref}">{note.citation}</a>&nbsp;'
                s += self.contentToStr(note.content)
                s += '</p>\n'
            s += '</div>'

        return s


HTML_HEAD = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title></title>
%s
</head>
<body>

"""

HTML_TAIL = """
</body>
</html>
"""
