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


class Document:

    def __init__(self, odtfilename):
        self.odtfilename = odtfilename

        self.styles = {}
        self.paragraps = []
        self.notes = []

    def get_style_by_display_name(self, display_name):
        for style in self.styles.values():
            if style.get_display_name(True) == display_name:
                return style
        raise Exception(f'No style found for name "{display_name}"')
