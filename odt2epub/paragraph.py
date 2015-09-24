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


class Paragraph:

    def __init__(self, attrs, styles, header=False):

        self.styles = styles
        self.style = styles[attrs.getValue('text:style-name')]

        self.content = []

        # This properties are used if this paragraph is a header
        self.isHeader = header
        self.headerlevel = 1
        if self.isHeader:
            if 'text:outline-level' in attrs:
                self.headerlevel = attrs.get('text:outline-level')
        else:
            if self.style.isHeader:
                self.isHeader = True
                self.headerlevel = self.style.headerlevel

    def append(self, content, stylename):
        style = self.styles.get(stylename)
        self.content.append((content, style))
