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


class Style:

    def __init__(self, name, attrs, styles, mappingstyles):
        self.name = name
        self.attrs = attrs

        self.parent = None
        if 'style:parent-style-name' in attrs:
            parentName = attrs.getValue('style:parent-style-name')
            self.parent = styles[parentName]

        self.mappingstyle = mappingstyles.get(name, '')

        # Header
        # I'm not sure about this heuristic
        self.isHeader = False
        if name.startswith('Heading'):
            self.isHeader = True
            self.headerlevel = 1
        else:
            parent = self.parent
            while(parent != None):
                if parent.isHeader:
                    self.isHeader = True
                    self.headerlevel = parent.headerlevel
                    break
                parent = parent.parent

        # Italic
        self.isItalic = False
        parent = self.parent
        while(parent != None):
            if parent.isItalic:
                self.isItalic = True
                break
            parent = parent.parent

        # Bold
        self.isBold = False
        parent = self.parent
        while(parent != None):
            if parent.isBold:
                self.isBold = True
                break
            parent = parent.parent

        # Align
        self.align = 'justify'
        parent = self.parent
        while(parent != None):
            if parent.align != 'justify':
                self.align = self.parent.align
                break
            parent = parent.parent

    def setProperties(self, properties):
        if 'fo:font-style' in properties.keys() and 'italic' == properties['fo:font-style']:
            self.isItalic = True

        if 'fo:font-weight' in properties.keys() and 'bold' == properties['fo:font-weight']:
            self.isBold = True

        if 'fo:text-align' in properties.keys():
            self.align = properties['fo:text-align']
            if self.align == 'end':
                self.align = 'right'
