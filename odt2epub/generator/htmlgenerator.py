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

        self.htmltxt = None
        self.cssrelfilename = None
        self._reset()

    def _reset(self):
        self.cssclass_to_export = []
        self.note_to_export = []
        self.toc_id_counter = 0
        self.pages = []
        self.htmltxt = None
        self.cssrelfilename = None

    def get_html(self, cssrelfilename):
        self._reset()
        self.cssrelfilename = cssrelfilename

        self.start_newpage()

        self.paragraphs_to_str(self.document.paragraps)

        self.close_newpage()

        stylesheetgenerator = StylesheetGenerator(self.document, self.cssclass_to_export, self.verbose)
        csstxt = stylesheetgenerator.get_stylesheet()

        return (self.pages, csstxt)

    def start_newpage(self):
        self.htmltxt = HTML_HEAD % f'<link href="{self.cssrelfilename}" rel="stylesheet" type="text/css" />'

    def close_newpage(self):

        self.htmltxt += self.notes_to_str()
        self.htmltxt += HTML_TAIL

        idx = len(self.pages) + 1
        chp = f'000{idx}'[-3:]
        pagename = f'chp{chp}.xhtml'
        self.pages.append((idx, pagename, self.htmltxt))

        self.htmltxt = None

    # def getHTML(self, cssrelfilename):
    #     htmltxt = HTML_HEAD % f'<link href="{cssrelfilename}" rel="stylesheet" type="text/css" />'
    #
    #     htmltxt += self.paragraphs_to_str(self.document.paragraps)
    #     htmltxt += self.notes_to_str()
    #
    #     htmltxt += HTML_TAIL
    #
    #     return htmltxt

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

        # print(sorted(set(self.cssclass_to_export)))

        if self.export_css:
            self.write_css(cssfilename)

    def write_css(self, cssfilename):

        stylesheetgenerator = StylesheetGenerator(self.document, self.cssclass_to_export, self.verbose)
        csstxt = stylesheetgenerator.get_stylesheet()

        with open(cssfilename, 'w', encoding='utf-8') as fout:
            fout.write(csstxt)

    def paragraphs_to_str(self, paragraps):

        for paragraph in paragraps:
            if paragraph.has_pagebreak_before():
                # print('!!!!!!! page break')
                self.close_newpage()
                self.start_newpage()

            if isinstance(paragraph, Header):
                line = self.header_to_str(paragraph)
            elif isinstance(paragraph, List):
                line = self.list_to_str(paragraph)
            else:
                line = self.paragraph_to_str(paragraph)
            # print(line)
            self.htmltxt += '%s\n' % line

        return self.htmltxt

    def list_to_str(self, list_):
        if list_.list_style == 'number':
            htmltxt = '<ol>\n'
        else:
            htmltxt = '<ul>\n'

        for listitem in list_.items:
            htmltxt += '<li>\n' + self.paragraphs_to_str(listitem.paragraps) + '</li>\n'

        if list_.list_style == 'number':
            htmltxt += '</ol>\n'
        else:
            htmltxt += '</ul>\n'

        return htmltxt

    def header_to_str(self, header):

        cssclass = header.get_style_display_name()
        self.cssclass_to_export.append(cssclass)

        self.toc_id_counter += 1

        s = f'<h{header.get_level()} id="hid_{self.toc_id_counter}">'
        s += self.content_to_str(header.content)
        s += f'</h{header.get_level()}>'
        return s

    def paragraph_to_str(self, paragraph):
        cssclass = paragraph.get_style_display_name()

        # if cssclass == 'Quotations':
        #     print(cssclass, self.lastParagraphClass)

        if self.keep_css_class and cssclass != 'Text body':
            # style = self.document.styles[cssclass]
            # if 'loext:contextual-spacing' in style.properties and style.properties['loext:contextual-spacing'].upper() == 'TRUE':
            #     print(cssclass, self.lastParagraphClass)
            selector = cssclass.lower().replace(' ', '_')
            s = f'<p class="{selector}">'
            self.cssclass_to_export.append(cssclass)
        else:
            s = '<p>'
        s += self.content_to_str(paragraph.content)
        s += '</p>'
        if s == '<p></p>':
            s = '<p class="emptyline">&nbsp;</p>'

        # self.lastParagraphClass = cssclass

        return s

    def content_to_str(self, content):
        s = ''
        for typ, text, style in content:
            if typ == 'str':
                if style:  # Start style
                    if style.is_italic(self.keep_css_class):
                        s += '<i>'
                    if style.is_bold():
                        s += '<b>'

                s += text

                if style:  # End style
                    if style.is_bold():
                        s += '</b>'
                    if style.is_italic(self.keep_css_class):
                        s += '</i>'
            elif typ == 'note':
                note = text
                ref = note.id.replace('ftn', 'refn')
                s += f'<sup><a id="{ref}" href="#{note.id}">{note.citation}</a></sup>'
                self.note_to_export.append(note)
            elif typ == 'line-break':
                s += '<br/>'
            else:
                raise Exception(f'Unhandled content type: {typ}')
        return s

    def notes_to_str(self):
        s = ''

        if len(self.note_to_export) > 0:
            s = '<div class="notes">\n'
            for note in self.note_to_export:
                ref = note.id.replace('ftn', 'refn')
                s += f'<p class="note"><a id="{note.id}" href="#{ref}">{note.citation}</a>&nbsp;'
                s += self.content_to_str(note.content)
                s += '</p>\n'
            s += '</div>'

        self.note_to_export.clear()

        return s


HTML_HEAD = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE htmltxt PUBLIC "-//W3C//DTD XHTML 1.1//EN"
    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

<htmltxt xmlns="http://www.w3.org/1999/xhtml">
<head>
<title></title>
%s
</head>
<body>

"""

HTML_TAIL = """
</body>
</htmltxt>
"""
