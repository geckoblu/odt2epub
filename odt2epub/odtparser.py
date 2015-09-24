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
from odt2epub.generator.htmlgenerator import HTMLGenerator
from odt2epub.taghandler import TagHandler


class OdtParser:

    def __init__(self, args):
        self.args = args

        self.odtfilename = args.odtfilename
        self.verbose = args.verbose

    def parse(self):
        if self.verbose > 0:
            print(_gt('Parsing: %s') % self.odtfilename)

        with zipfile.ZipFile(self.odtfilename) as odtfile:
            tagHandler = TagHandler(self.args)

            ostr = odtfile.read('styles.xml')
            parse(BytesIO(ostr), tagHandler)

            ostr = odtfile.read('content.xml')
            parse(BytesIO(ostr), tagHandler)

        generator = HTMLGenerator(tagHandler, self.args)
        generator.write()
