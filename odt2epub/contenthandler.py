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
import sys

import xml.sax.handler


class Paragraph:

    def __init__(self, style, attrs):
        self.style = style
        self.attrs = attrs

        self.content = []

    def append(self, typ, content, style):
        self.content.append((typ, content, style))

    def get_style_display_name(self):
        return self.style.get_display_name()

    def has_pagebreak_before(self):
        return self.style.has_pagebreak_before()


class Header(Paragraph):

    def get_level(self):
        return self.attrs.get('text:outline-level')


class List():

    def __init__(self, list_style):
        self.list_style = list_style

        self.items = []

    def append(self, listitem):
        self.items.append(listitem)


class ListItem():

    def __init__(self):
        self.paragraps = []

    def append(self, paragrap):
        self.paragraps.append(paragrap)


class Note:

    def __init__(self, attrs):
        self.noteclass = attrs['text:note-class']
        self.id = attrs['text:id']

        self.citation = ''
        self.content = []

    def set_citation(self, citation):
        self.citation = citation

    def append(self, typ, content, style):
        self.content.append((typ, content, style))


class ContentHandler(xml.sax.handler.ContentHandler):

    def __init__(self, odtfilename, document):
        super().__init__()
        self.odtfilename = odtfilename
        self.styles = document.styles
        self.paragraps = document.paragraps
        self.notes = document.notes

        self.current_paragraph = None
        self.current_span_style = None
        self.current_list = None
        self.current_list_item = None

        self.current_note = None
        self.current_note_citation = False

        self.debug_current_list_with_continue_numbering = False

    def startElement(self, name, attrs):
        # print("startElement " + name)
        if name == 'text:h':
            style = self.styles[attrs['text:style-name']]
            self.current_paragraph = Header(style, attrs)
            self.paragraps.append(self.current_paragraph)
        elif name == 'text:note':
            self.current_note = Note(attrs)
        elif name == 'text:note-citation':
            self.current_note_citation = True
        elif name == 'text:p':
            if self.current_note:
                pass
            else:
                style = self.styles[attrs['text:style-name']]
                self.current_paragraph = Paragraph(style, attrs)
                if self.current_list_item:
                    self.current_list_item.append(self.current_paragraph)
                else:
                    self.paragraps.append(self.current_paragraph)
        elif name == 'text:span':
            self.current_span_style = self.styles[attrs['text:style-name']]
        elif name == 'text:list':
            if 'text:continue-numbering' in attrs:
                sys.stderr.write('!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
                sys.stderr.write(f'Current List With Continue Numbering: {self.odtfilename}\n')
                self.debug_current_list_with_continue_numbering = True
            style = self.styles[attrs['text:style-name']]
            self.current_list = List(style.properties['list-style'])
            self.paragraps.append(self.current_list)
        elif name == 'text:list-item':
            self.current_list_item = ListItem()
            self.current_list.append(self.current_list_item)
        elif name == 'text:line-break':
            self.current_paragraph.append('line-break', '', None)

    def endElement(self, name):
        # print("endElement " + name)
        if name == 'text:note':
            self.notes.append(self.current_note)
            self.current_paragraph.append('note', self.current_note, None)
            self.current_note = None
        elif name == 'text:note-citation':
            self.current_note_citation = False
        elif name == 'text:p':
            if self.current_note:
                pass
            else:
                if self.debug_current_list_with_continue_numbering:
                    sys.stderr.write(f'\t-> {self.current_paragraph.content[0][0]}\n')
                    self.debug_current_list_with_continue_numbering = False
                self.current_paragraph = None
        elif name == 'text:span':
            self.current_span_style = None
        elif name == 'text:list':
            self.current_list = None
        elif name == 'text:list-item':
            self.current_list_item = None

    def characters(self, content):
        # print("\t\t" + content)
        if self.current_note_citation:
            self.current_note.set_citation(content)
        elif self.current_note:
            self.current_note.append('str', content, self.current_span_style)
        elif self.current_paragraph:
            self.current_paragraph.append('str', content, self.current_span_style)
        else:
            sys.stderr.write('WARNING: Unhandled content: %s\n' % content)
