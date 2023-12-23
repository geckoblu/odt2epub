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
        
    def append(self, content, style):
        self.content.append((content, style))
        
    def getStyleDisplayName(self):
        return self.style.getDisplayName()

class Header(Paragraph):
    
    def getLevel(self):
        return self.attrs.get('text:outline-level')

class ContentHandler(xml.sax.handler.ContentHandler):

    def __init__(self, styles, paragraps):
        super().__init__()
        self.styles = styles
        self.paragraps = paragraps
        
        self.currentParagraph = None
        self.currentSpanStyle = None

    def startElement(self, name, attrs):
        if name == 'text:h':
            style = self.styles[attrs['text:style-name']]
            self.currentParagraph = Header(style, attrs)
            self.paragraps.append(self.currentParagraph)
        elif name == 'text:p':
            style = self.styles[attrs['text:style-name']]
            self.currentParagraph = Paragraph(style, attrs)
            self.paragraps.append(self.currentParagraph)
        elif name == 'text:span':
            self.currentSpanStyle = self.styles[attrs['text:style-name']]
        elif name == 'text:line-break':
            pass

    def endElement(self, name):
        if name == 'text:p':
            self.currentParagraph = None
        elif name == 'text:span':
            self.currentSpanStyle = None
    
    def characters(self, content):
        if self.currentParagraph:
            self.currentParagraph.append(content, self.currentSpanStyle)
        else:
            sys.stderr.write('WARNING: Unhandled content: %s\n' % content)
