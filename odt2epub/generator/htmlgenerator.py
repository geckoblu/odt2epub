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

    def __init__(self, document, flat_html, verbose=0):
        self.document = document
        self.verbose = verbose
        self.flat_html = flat_html

        # self.inline_css = args.inline_css
        # self.insert_sigil_toc_id = args.insert_sigil_toc_id
        # self.insert_split_marker = args.insert_split_marker

        self.htmltxt = None
        self.cssrelfilename = None
        self.current_pagename = None
        self.current_tocelement = None
        self._reset()

    def _reset(self):
        self.cssclass_to_export = []
        self.note_to_export = []
        self.toc_id_counter = 0
        self.pages = []
        self.current_pagename = None
        self.toc = TocElement(None, 0, '', '', 'root')
        self.current_tocelement = self.toc
        self.htmltxt = None
        self.cssrelfilename = None

    def get_html(self, cssrelfilename):
        self._reset()
        self.cssrelfilename = cssrelfilename

        self._start_newpage()

        self._paragraphs_to_str(self.document.paragraps)

        self._close_newpage()

        stylesheetgenerator = StylesheetGenerator(self.document, self.cssclass_to_export, self.verbose)
        csstxt = stylesheetgenerator.get_stylesheet()

        return (self.pages, csstxt, self.toc)

    def _start_newpage(self):
        self.htmltxt = HTML_HEAD % f'<link href="{self.cssrelfilename}" rel="stylesheet" type="text/css" />'

        idx = len(self.pages) + 1
        chp = f'000{idx}'[-3:]
        self.current_pagename = f'chp{chp}.xhtml'

    def _close_newpage(self):

        self.htmltxt += self._notes_to_str()
        self.htmltxt += HTML_TAIL

        idx = len(self.pages) + 1
        self.pages.append((idx, self.current_pagename, self.htmltxt))

        self.htmltxt = None

    def write(self, htmlfilename):
        if self.verbose > 0:
            print(_gt('Output:  %s') % htmlfilename)

        fname, __ = os.path.splitext(htmlfilename)
        basename, __ = os.path.split(fname)
        cssfilename = '%s.css' % fname
        cssrelfilename = f'./{basename}.css'

        pages, stylesheet, toc = self.get_html(cssrelfilename)

        if len(pages) != 1:
            raise Exception(f'Something went wrong in generating HTML (n° of pages {len(pages)} !=1)')

        htmlpage = pages[0][2]
        htmlpage = htmlpage.replace('<title></title>', f'<title>{basename}</title>')

        with open(htmlfilename, 'w', encoding='utf-8') as fout:
            fout.write(htmlpage)

        with open(cssfilename, 'w', encoding='utf-8') as fout:
            fout.write(stylesheet)

    def _paragraphs_to_str(self, paragraps):

        for paragraph in paragraps:
            if not self.flat_html and paragraph.has_pagebreak_before():
                # print('!!!!!!! page break')
                self._close_newpage()
                self._start_newpage()

            if isinstance(paragraph, Header):
                line = self._header_to_str(paragraph)
            elif isinstance(paragraph, List):
                line = self._list_to_str(paragraph)
            else:
                line = self._paragraph_to_str(paragraph)
            # print(line)
            self.htmltxt += '%s\n' % line

        return self.htmltxt

    def _list_to_str(self, list_):
        if list_.list_style == 'number':
            htmltxt = '<ol>\n'
        else:
            htmltxt = '<ul>\n'

        for listitem in list_.items:
            htmltxt += '<li>\n' + self._paragraphs_to_str(listitem.paragraps) + '</li>\n'

        if list_.list_style == 'number':
            htmltxt += '</ol>\n'
        else:
            htmltxt += '</ul>\n'

        return htmltxt

    def _header_to_str(self, header):

        cssclass = header.get_style_display_name()
        self.cssclass_to_export.append(cssclass)

        self.toc_id_counter += 1

        level = header.get_level()
        hid = f'hid_{self.toc_id_counter}'
        label = self._content_to_str(header.content)

        s = f'<h{level} id="{hid}">'
        s += label
        s += f'</h{level}>'

        # Generate TOC Element
        label = label.replace('<br/>', ' ')
        # print(level, self.current_pagename, hid, label)
        parent = self.current_tocelement.get_parent_for_level(level)
        # print(parent.label, '->', label)
        self.current_tocelement = TocElement(parent, level, self.current_pagename, hid, label)
        parent.add_child(self.current_tocelement)

        return s

    def _paragraph_to_str(self, paragraph):
        cssclass = paragraph.get_style_display_name()

        # if cssclass == 'Quotations':
        #     print(cssclass, self.lastParagraphClass)

        if cssclass != 'Text body':
            # style = self.document.styles[cssclass]
            # if 'loext:contextual-spacing' in style.properties and style.properties['loext:contextual-spacing'].upper() == 'TRUE':
            #     print(cssclass, self.lastParagraphClass)
            selector = cssclass.lower().replace(' ', '_')
            s = f'<p class="{selector}">'
            self.cssclass_to_export.append(cssclass)
        else:
            s = '<p>'
        s += self._content_to_str(paragraph.content)
        s += '</p>'
        if s == '<p></p>':
            s = '<p class="emptyline">&nbsp;</p>'

        # self.lastParagraphClass = cssclass

        return s

    def _content_to_str(self, content):
        s = ''
        for typ, text, style in content:
            if typ == 'str':
                if style:  # Start style
                    if style.is_italic(True):
                        s += '<i>'
                    if style.is_bold():
                        s += '<b>'

                s += text

                if style:  # End style
                    if style.is_bold():
                        s += '</b>'
                    if style.is_italic(True):
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

    def _notes_to_str(self):
        s = ''

        if len(self.note_to_export) > 0:
            s = '<div class="notes">\n'
            for note in self.note_to_export:
                ref = note.id.replace('ftn', 'refn')
                s += f'<p class="note"><a id="{note.id}" href="#{ref}">{note.citation}</a>&nbsp;'
                s += self._content_to_str(note.content)
                s += '</p>\n'
            s += '</div>'

        self.note_to_export.clear()

        return s


class TocElement():

    def __init__(self, parent, level, pagename, hid, label):
        self.parent = parent
        self.level = int(level)
        self.pagename = pagename
        self.hid = hid
        self.label = label
        self.children = []

    def get_parent_for_level(self, level):
        level = int(level)
        if level > self.level:
            return self
        elif level == self.level:
            return self.parent
        else:
            return self.parent.get_parent_for_level(level)

    def add_child(self, child):
        self.children.append(child)


HTML_HEAD = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE htmltxt PUBLIC "-//W3C//DTD XHTML 1.1//EN"
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
