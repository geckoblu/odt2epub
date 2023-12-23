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


class HTMLParagraph:

    def __init__(self, paragraph, keep_css_class, insert_split_marker):
        self.p = paragraph
        self.keep_css_class = keep_css_class
        self.insert_split_marker = insert_split_marker

    def _getlevel(self):
        if self.p.isHeader:
            return 'h%s' % self.p.headerlevel
        else:
            return 'p'

    def _getclss(self):
        clss = ''

        if not self.p.isHeader:
            if self.p.style.align == 'right':
                clss = ' class="right"'
            elif self.p.style.align == 'center':
                clss = ' class="center"'

            if self.keep_css_class:
                clss = ' class="%s"' % self.p.style.name

            if self.p.style.mappingstyle:
                clss = ' class="%s"' % self.p.style.mappingstyle

        return clss

    def __repr__(self):

        s = '<%s%s>' % (self._getlevel(), self._getclss())

        if self.p.isHeader and self.insert_split_marker and self.p.headerlevel == 1:
            s = '<hr class="sigil_split_marker" />\n' + s

        if not self.p.isHeader:
            if self.p.style.isItalic:
                s += '<i>'
            if self.p.style.isBold:
                s += '<b>'

        for content, style in self.p.content:
            if style:
                if style.isItalic:
                    s += '<i>'
                if style.isBold:
                    s += '<b>'

            s += content

            if style:
                if style.isBold:
                    s += '</b>'
                if style.isItalic:
                    s += '</i>'

        if not self.p.isHeader:
            if self.p.style.isBold:
                s += '</b>'
            if self.p.style.isItalic:
                s += '</i>'

        s += '</%s>' % self._getlevel()

        return s
