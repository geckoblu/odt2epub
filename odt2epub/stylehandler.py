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
        self.has_local_properties_flag = False
        self.set_properties(attrs)

    def set_properties(self, properties):
        for key, value in properties.items():
            self.properties[key] = value
        # if 'fo:font-style' in properties.keys() and properties['fo:font-style'] == 'italic':
        #     print(properties['fo:font-style'])
        #     self.is_italic = True
        #
        # if 'fo:font-weight' in properties.keys() and properties['fo:font-weight'] == 'bold':
        #     self.is_bold = True
        #
        # if 'fo:text-align' in properties:
        #     # print(properties['fo:text-align'])
        #     self.align = properties['fo:text-align']
        #     if self.align == 'end':
        #         self.align = 'right'

    def has_local_properties(self):
        return self.has_local_properties_flag

    def get_display_name(self, local=False):
        if 'style:display-name' in self.properties:
            return self.properties['style:display-name']
        else:
            if self.automatic and self.parent and not local:
                return self.parent.get_display_name()
            else:
                return self.name

    def get_font_style(self, local=False):
        if 'fo:font-style' in self.properties:
            return self.properties['fo:font-style']
        else:
            if self.parent and not local:
                return self.parent.get_font_style()
            else:
                return None

    def is_italic(self, local=False):
        return self.get_font_style(local) == 'italic'

    def get_font_weight(self, local=False):
        if 'fo:font-weight' in self.properties:
            return self.properties['fo:font-weight']
        else:
            if self.parent and not local:
                return self.parent.get_font_weight()
            else:
                return None

    def is_bold(self, local=False):
        return self.get_font_weight(local) == 'bold'

    def get_header_level(self):
        return self.properties['style:default-outline-level']

    def get_alignment(self, local=False):
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
                return self.parent.get_alignment()
            else:
                return None

    def has_pagebreak_before(self):
        try:
            return self.properties['fo:break-before'] == 'page'
        except KeyError:
            return False

    def get_css_properties(self):
        properties = []

        alignment = self.get_alignment()
        if alignment:
            properties.append(('text-align', alignment))

        font_style = self.get_font_style()
        if font_style:
            properties.append(('font-style', font_style))

        font_weight = self.get_font_weight()
        if font_weight:
            properties.append(('font-weight', font_weight))

        return properties


class StyleHandler(ContentHandler):

    def __init__(self, odtfilename, styles, automatic):
        super().__init__()
        self.odtfilename = odtfilename
        self.styles = styles
        self.automatic = automatic

        self.current_style = None

    def startElement(self, name, attrs):
        # print('-' * 20)
        # print(name, attrs.getNames())
        # print(name)

        if name == 'style:style':
            assert (self.current_style is None), 'Unexpected nested <style:style>'
            assert (self.styles.get(attrs['style:name']) is None), 'Unexpected duplicated style name %s.' % attrs['style:name']

            parent = self.styles.get(attrs.get('style:parent-style-name'))
            style = Style(attrs, parent, self.automatic)

            # if style.name == 'P2':
            #     print(attrs.get('style:parent-style-name'))

            self.current_style = style
            self.styles[style.name] = self.current_style
        elif name in ('style:text-properties', 'style:paragraph-properties'):
            if self.current_style:
                self.current_style.set_properties(attrs)
        elif name == 'text:list-style':
            style = Style(attrs, None, self.automatic)
            self.current_style = style
            self.styles[style.name] = self.current_style
        elif name == 'text:list-level-style-number':
            self.current_style.set_properties({'list-style':'number'})
        elif name == 'text:list-level-style-bullet':
            self.current_style.set_properties({'list-style':'bullet'})

    def endElement(self, name):
        if name == 'style:style':
            self.current_style = None
