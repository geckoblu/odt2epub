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
from io import BytesIO
from xml.sax import parse
import zipfile

from odt2epub import _gt
from odt2epub.stylehandler import StyleHandler
from odt2epub.contenthandler import ContentHandler
from odt2epub.document import Document


class OdtParser:

    def __init__(self):
        pass

    def parse(self, txtfilename, verbose=0):
        if verbose > 0:
            print(_gt('Parsing: %s') % txtfilename)

        document = Document(txtfilename)

        with zipfile.ZipFile(txtfilename) as odtfile:

            ostr = odtfile.read('styles.xml')
            parse(BytesIO(ostr), StyleHandler(txtfilename, document.styles, False))

            ostr = odtfile.read('content.xml')
            parse(BytesIO(ostr), StyleHandler(txtfilename, document.styles, True))
            parse(BytesIO(ostr), ContentHandler(txtfilename, document))

        return document
