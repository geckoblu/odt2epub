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

from odt2epub import _gt
from odt2epub.document import Document
from odt2epub.contenthandler import Paragraph
from odt2epub.stylehandler import Style


class TxtParser:

    def __init__(self):
        pass

    def parse(self, txtfilename, verbose=0):
        if verbose > 0:
            print(_gt('Parsing: %s') % txtfilename)

        attrs = {}
        attrs['style:name'] = 'Text body'
        txtstyle = Style(attrs, None, False)

        document = Document(txtfilename)
        document.styles[txtstyle.name] = txtstyle

        paragraph = Paragraph(txtstyle, None)

        with open(txtfilename, 'r') as infile:
            for line in infile:
                line = line.strip()
                # import sys
                # print('* ' + line)
                if line == '':
                    document.paragraps.append(paragraph)
                    paragraph = Paragraph(txtstyle, None)
                else:
                    paragraph.append('str', line + ' ')
                    

        # paragraph = Paragraph(txtstyle, None)
        # paragraph.append('str', 'Lorem ipsum')
        document.paragraps.append(paragraph)

        return document
