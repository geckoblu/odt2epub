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
from xml.sax.handler import ContentHandler


class Style:

    def __init__(self, attrs, parent, automatic):
        self.name = attrs['style:name']
        self.parent = parent
        self.automatic = automatic

        self.properties = {}
        self.hasLocalPropertiesFlag = False
        self.setProperties(attrs)

    def setProperties(self, properties):
        for key, value in properties.items():
            self.properties[key] = value
        # if 'fo:font-style' in properties.keys() and properties['fo:font-style'] == 'italic':
        #     print(properties['fo:font-style'])
        #     self.isItalic = True
        #
        # if 'fo:font-weight' in properties.keys() and properties['fo:font-weight'] == 'bold':
        #     self.isBold = True
        #
        # if 'fo:text-align' in properties:
        #     # print(properties['fo:text-align'])
        #     self.align = properties['fo:text-align']
        #     if self.align == 'end':
        #         self.align = 'right'

    def hasLocalProperties(self):
        return self.hasLocalPropertiesFlag

    def getDisplayName(self, local=False):
        if 'style:display-name' in self.properties:
            return self.properties['style:display-name']
        else:
            if self.automatic and self.parent and not local:
                return self.parent.getDisplayName()
            else:
                return self.name

    def getFontStyle(self, local=False):
        if 'fo:font-style' in self.properties:
            return self.properties['fo:font-style']
        else:
            if self.parent and not local:
                return self.parent.getFontStyle()
            else:
                return None

    def isItalic(self, local=False):
        return self.getFontStyle(local) == 'italic'

    def getFontWeight(self, local=False):
        if 'fo:font-weight' in self.properties:
            return self.properties['fo:font-weight']
        else:
            if self.parent and not local:
                return self.parent.getFontWeight()
            else:
                return None

    def isBold(self, local=False):
        return self.getFontWeight(local) == 'bold'

    def getHeaderLevel(self):
        try:
            return self.properties['style:default-outline-level']
        except KeyError:
            return self.getDisplayName()[len('Heading'):].strip()

    def getAlignment(self, local=False):
        if 'fo:text-align' in self.properties:
            alignment = self.properties['fo:text-align']
            if alignment == 'start':
                return 'left'
            elif alignment == 'end':
                return 'right'
            else:
                return alignment
        else:
            if self.parent and not local:
                return self.parent.getAlignment()
            else:
                return None

    def get_css_properties(self):
        properties = []

        alignment = self.getAlignment()
        if alignment:
            properties.append(('text-align', alignment))

        fontStyle = self.getFontStyle()
        if fontStyle:
            properties.append(('font-style', fontStyle))

        fontWeight = self.getFontWeight()
        if fontWeight:
            properties.append(('font-weight', fontWeight))

        return properties


class StyleHandler(ContentHandler):

    def __init__(self, odtfilename, styles, automatic):
        super().__init__()
        self.odtfilename = odtfilename
        self.styles = styles
        self.automatic = automatic

        self.currentStyle = None

    def startElement(self, name, attrs):
        # print('-' * 20)
        # print(name, attrs.getNames())
        # print(name)

        if name == 'style:style':
            assert (self.currentStyle is None), 'Unexpected nested <style:style>'
            assert (self.styles.get(attrs['style:name']) is None), 'Unexpected duplicated style name %s.' % attrs['style:name']

            parent = self.styles.get(attrs.get('style:parent-style-name'))
            style = Style(attrs, parent, self.automatic)

            # if style.name == 'P2':
            #     print(attrs.get('style:parent-style-name'))

            self.currentStyle = style
            self.styles[style.name] = self.currentStyle
        elif name in ('style:text-properties', 'style:paragraph-properties'):
            if self.currentStyle:
                self.currentStyle.setProperties(attrs)
        elif name == 'text:list-style':
            style = Style(attrs, None, self.automatic)
            self.currentStyle = style
            self.styles[style.name] = self.currentStyle
        elif name == 'text:list-level-style-number':
            self.currentStyle.setProperties({'list-style':'number'})
        elif name == 'text:list-level-style-bullet':
            self.currentStyle.setProperties({'list-style':'bullet'})

    def endElement(self, name):
        if name == 'style:style':
            self.currentStyle = None
