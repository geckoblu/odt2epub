import os
import uuid
import zipfile

from odt2epub import _gt
from odt2epub.generator.htmlgenerator import HTMLGenerator


class EpubWriter:

    def __init__(self, document, verbose=0):
        self.document = document
        self.verbose = verbose

        self.playorder = 0
        self.toctxt = ''

    def write(self, epubfilename):
        if self.verbose > 0:
            print(_gt('Output:  %s') % epubfilename)

        fname, __ = os.path.splitext(epubfilename)
        basename, __ = os.path.split(fname)

        epubuuid = uuid.uuid4()

        generator = HTMLGenerator(self.document, flat_html=False, verbose=self.verbose)
        pages, stylesheet, toc = generator.get_html('../Styles/stylesheet.css')

        epub = zipfile.ZipFile(epubfilename, 'w')
        epub.writestr("mimetype", "application/epub+zip")
        epub.writestr("META-INF/container.xml", CONTAINER_XML)

        manifest = ''
        spine = ''
        for _idx, chpname, html in pages:
            manifest += f'    <item id="{chpname}" href="Text/{chpname}" media-type="application/xhtml+xml"/>'
            spine += f'    <itemref idref="{chpname}"/>\n'
            epub.writestr(f"OEBPS/Text/{chpname}", html)

        epub.writestr("OEBPS/content.opf", CONTENT_OPF % {'title':basename, 'manifest':manifest, 'spine':spine, 'epubuuid':epubuuid})

        toctxt = self._generate_toc(toc)
        epub.writestr("OEBPS/toc.ncx", TOC_NCX % {'navpoints':toctxt, 'epubuuid':epubuuid})

        epub.writestr("OEBPS/Styles/stylesheet.css", stylesheet)

    def _generate_toc(self, toc_root):

        self.playorder = 0
        self.toctxt = ''

        for child in toc_root.children:
            self._generate_navpoint(child)

        return self.toctxt

    def _generate_navpoint(self, tocelement):
        self.playorder += 1

        indt = '  ' * tocelement.level
        self.toctxt += f'{indt}<navPoint id="navPoint-{self.playorder}" playOrder="{self.playorder}">\n'
        self.toctxt += f'{indt}  <navLabel><text>{tocelement.label}</text></navLabel>\n'
        self.toctxt += f'{indt}  <content src="Text/{tocelement.pagename}#{tocelement.hid}" />\n'

        for child in tocelement.children:
            self._generate_navpoint(child)

        self.toctxt += f'{indt}</navPoint>\n'


CONTAINER_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
   </rootfiles>
</container>'''

CONTENT_OPF = '''<?xml version="1.0" encoding="utf-8"?>
<package version="2.0" unique-identifier="BookId" xmlns="http://www.idpf.org/2007/opf">
  <metadata xmlns:opf="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier opf:scheme="UUID" id="BookId">urn:uuid:%(epubuuid)s</dc:identifier>
    <dc:title>%(title)s</dc:title>
    <dc:language>it</dc:language>
    <meta content="1.1.0" name="Sigil version" />
    <dc:date xmlns:opf="http://www.idpf.org/2007/opf" opf:event="modification">2024-02-21</dc:date>
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <item id="stylesheet.css" href="Styles/stylesheet.css" media-type="text/css"/>
%(manifest)s  </manifest>
  <spine toc="ncx">
%(spine)s  </spine>
</package>'''

TOC_NCX = '''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"
   "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="urn:uuid:%(epubuuid)s" />
    <meta name="dtb:depth" content="0" />
    <meta name="dtb:totalPageCount" content="0" />
    <meta name="dtb:maxPageNumber" content="0" />
  </head>
<docTitle>
  <text>Unknown</text>
</docTitle>
<navMap>
%(navpoints)s</navMap>
</ncx>'''
