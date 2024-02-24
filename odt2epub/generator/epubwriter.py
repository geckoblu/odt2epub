import re
import zipfile
# from bs4 import BeautifulSoup

from odt2epub import _gt
from odt2epub.generator.htmlgenerator import HTMLGenerator


class EpubWriter:

    def __init__(self, document, verbose=0):
        self.document = document
        self.verbose = verbose

    def write(self, epubfilename):
        if self.verbose > 0:
            print(_gt('Output:  %s') % epubfilename)

        generator = HTMLGenerator(self.document, verbose=self.verbose)
        pages, stylesheet = generator.get_html('../Styles/stylesheet.css')

        epub = zipfile.ZipFile(epubfilename, 'w')
        epub.writestr("mimetype", "application/epub+zip")
        epub.writestr("META-INF/container.xml", CONTAINER_XML)

        manifest = ''
        spine = ''
        for _idx, chpname, html in pages:
            manifest += f'    <item id="{chpname}" href="Text/{chpname}" media-type="application/xhtml+xml"/>'
            spine += f'    <itemref idref="{chpname}"/>\n'
            epub.writestr(f"OEBPS/Text/{chpname}", html)

        epub.writestr("OEBPS/content.opf", CONTENT_OPF % {'manifest':manifest, 'spine':spine})

        toc = self._generate_toc(pages)
        epub.writestr("OEBPS/toc.ncx", toc)

        epub.writestr("OEBPS/Styles/stylesheet.css", stylesheet)

    def _grab_toc(self, pages):
        remover = re.compile('<.*?>')

        toc = []
        for __, chpname, html in pages:
            for match in re.finditer(r'<h(\d*?) id="(.*?)">(.*?)</h', html):
                level = match.group(1)
                hid = match.group(2)
                label = match.group(3).replace('<br/>', ' ')
                label = re.sub(remover, '', label)
                # soup = BeautifulSoup(match.group(3), "html.parser")
                # label = soup.text
                toc.append((level, hid, label, chpname))

        return toc

    def _generate_toc(self, pages):

        toc = self._grab_toc(pages)

        navpoints = ''
        for playorder, (level, hid, label, chpname) in enumerate(toc, start=1):
            ref = chpname
            navpoints += f'''<navPoint id="navPoint-{playorder}" playOrder="{playorder}">
  <navLabel>
    <text>{label}</text>
  </navLabel>
  <content src="Text/{ref}" />
</navPoint>
'''
        return TOC_NCX % {'navpoints':navpoints}


CONTAINER_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
   </rootfiles>
</container>'''

CONTENT_OPF = '''<?xml version="1.0" encoding="utf-8"?>
<package version="2.0" unique-identifier="BookId" xmlns="http://www.idpf.org/2007/opf">
  <metadata xmlns:opf="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier opf:scheme="UUID" id="BookId">urn:uuid:d0e46b7c-4ef8-4537-a901-312c3527c202</dc:identifier>
    <dc:language>en</dc:language>
    <dc:title>[Title here]</dc:title>
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
    <meta name="dtb:uid" content="urn:uuid:d0e46b7c-4ef8-4537-a901-312c3527c202" />
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
