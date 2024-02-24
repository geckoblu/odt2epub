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

    def getStyleDisplayName(self):
        return self.style.getDisplayName()
    
    def has_pagebreak_before(self):
        return self.style.has_pagebreak_before()


class Header(Paragraph):

    def getLevel(self):
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

    def setCitation(self, citation):
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

        self.currentParagraph = None
        self.currentSpanStyle = None
        self.currentList = None
        self.currentListItem = None

        self.currentNote = None
        self.currentNoteCitation = False

        self.debugCurrentListWithContinueNumbering = False

    def startElement(self, name, attrs):
        # print("startElement " + name)
        if name == 'text:h':
            style = self.styles[attrs['text:style-name']]
            self.currentParagraph = Header(style, attrs)
            self.paragraps.append(self.currentParagraph)
        elif name == 'text:note':
            self.currentNote = Note(attrs)
        elif name == 'text:note-citation':
            self.currentNoteCitation = True
        elif name == 'text:p':
            if self.currentNote:
                pass
            else:
                style = self.styles[attrs['text:style-name']]
                self.currentParagraph = Paragraph(style, attrs)
                if self.currentListItem:
                    self.currentListItem.append(self.currentParagraph)
                else:
                    self.paragraps.append(self.currentParagraph)
        elif name == 'text:span':
            self.currentSpanStyle = self.styles[attrs['text:style-name']]
        elif name == 'text:list':
            if 'text:continue-numbering' in attrs:
                sys.stderr.write('!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
                sys.stderr.write(f'Current List With Continue Numbering: {self.odtfilename}\n')
                self.debugCurrentListWithContinueNumbering = True
            style = self.styles[attrs['text:style-name']]
            self.currentList = List(style.properties['list-style'])
            self.paragraps.append(self.currentList)
        elif name == 'text:list-item':
            self.currentListItem = ListItem()
            self.currentList.append(self.currentListItem)
        elif name == 'text:line-break':
            self.currentParagraph.append('line-break', '', None)

    def endElement(self, name):
        # print("endElement " + name)
        if name == 'text:note':
            self.notes.append(self.currentNote)
            self.currentParagraph.append('note', self.currentNote, None)
            self.currentNote = None
        elif name == 'text:note-citation':
            self.currentNoteCitation = False
        elif name == 'text:p':
            if self.currentNote:
                pass
            else:
                if self.debugCurrentListWithContinueNumbering:
                    sys.stderr.write(f'\t-> {self.currentParagraph.content[0][0]}\n')
                    self.debugCurrentListWithContinueNumbering = False
                self.currentParagraph = None
        elif name == 'text:span':
            self.currentSpanStyle = None
        elif name == 'text:list':
            self.currentList = None
        elif name == 'text:list-item':
            self.currentListItem = None

    def characters(self, content):
        # print("\t\t" + content)
        if self.currentNoteCitation:
            self.currentNote.setCitation(content)
        elif self.currentNote:
            self.currentNote.append('str', content, self.currentSpanStyle)
        elif self.currentParagraph:
            self.currentParagraph.append('str', content, self.currentSpanStyle)
        else:
            sys.stderr.write('WARNING: Unhandled content: %s\n' % content)
