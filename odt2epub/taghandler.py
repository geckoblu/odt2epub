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
from xml.sax.handler import ContentHandler

from odt2epub.paragraph import Paragraph
from odt2epub.style import Style


class TagHandler(ContentHandler):

    def __init__(self, args):

        self.styles = {}
        self.paragraps = []

        self.mappingstyles = {}
        if args.map_style:
            for m in args.map_style:
                odtstyle, cssstyle = m.strip().split()
                self.mappingstyles[odtstyle.strip()] = cssstyle.strip()

        self.currentStyle = None
        self.currentParagraph = None
        self.currentSpanStyle = None

    def startElement(self, name, attrs):
        # print('-' * 20)
        # print(name, attrs.getNames())
        if name == 'style:style':
            assert (self.currentStyle == None), 'Unexpected nested <style:style>'
            styleName = attrs.getValue('style:name')
            assert (self.styles.get(styleName) == None), 'Unexpected duplicated style name %s.' % styleName
            self.currentStyle = Style(styleName, attrs, self.styles, self.mappingstyles)
            self.styles[styleName] = self.currentStyle
        elif name == 'style:text-properties' or name == 'style:paragraph-properties':
            if self.currentStyle:
                self.currentStyle.setProperties(attrs)
            # properties = self.styles.get(self.styleName)
        elif name == 'text:p':
            self.currentParagraph = Paragraph(attrs, self.styles)
            self.paragraps.append(self.currentParagraph)
        elif name == 'text:h':
            self.currentParagraph = Paragraph(attrs, self.styles, header=True)
            self.paragraps.append(self.currentParagraph)
        elif name == 'text:line-break':
            self.currentParagraph.append('<br />\n', self.currentSpanStyle)
        elif name == 'text:span':
            if 'text:style-name' in attrs:
                self.currentSpanStyle = attrs['text:style-name']

    def endElement(self, name):
        if name == 'style:style':
            self.currentStyle = None
        elif name == 'text:p':
            self.currentParagraph = None
        elif name == 'text:span':
            self.currentSpanStyle = None

    def characters(self, content):
        if self.currentParagraph:
            self.currentParagraph.append(content, self.currentSpanStyle)
        else:
            sys.stderr.write('WARNING: Unhandled content: %s\n' % content)
