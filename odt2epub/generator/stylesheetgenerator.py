import os
import sys


class StylesheetGenerator:

    def __init__(self, document, cssclassToExport, verbose):
        self.document = document
        self.verbose = verbose

        self._load_default_selectors()
        self._load_document_selectors(cssclassToExport)

    def _load_default_selectors(self):
        self.selectors = {}
        basedir, __ = os.path.split(__file__)
        cssfilename = os.path.join(basedir, 'stylesheet.css')
        with open(cssfilename) as cssinf:
            linenumber = 0
            for line in cssinf:
                linenumber += 1
                line = line.strip()
                if line == '':
                    continue

                if line.find('{') > 0:
                    selector = line[:line.find('{')].strip()
                    self.selectors[selector] = {}
                elif line.find('}') > -1:
                    selector = None
                elif line.find(':') > 0:
                    if selector is None:
                        sys.stderr.write(f"ERROR StylesheetGenerator: line outside selector {linenumber}: {line}\n")
                    attr = line[:line.find(':')]
                    value = line[line.find(':') + 1:].strip()
                    if value[-1] == ';':
                        self.selectors[selector][attr] = value[:-1]
                    else:
                        sys.stderr.write(f"ERROR StylesheetGenerator: missing ending semicolon {linenumber}: {line}\n")
                else:
                    sys.stderr.write(f"ERROR StylesheetGenerator: unable to parse line {linenumber}: {line}\n")

    def _load_document_selectors(self, docselectors):
        docselectors = sorted(set(docselectors))

        for docselector in docselectors:
            if self.verbose > 1:
                print('StylesheetGenerator:', '-' * 20)
                print('StylesheetGenerator:', 'Doc selector:', docselector)

            style = self.document.get_style_by_display_name(docselector)

            if docselector.startswith('Heading'):
                selector = f'h{style.get_header_level()}'
            else:
                selector = '.' + docselector.lower().replace(' ', '_')

            properties = self.selectors.get(selector, {})

            if self.verbose > 1:
                print('StylesheetGenerator:', 'CSS selector:', selector)
                print('StylesheetGenerator:', 'default properties:', properties)

            for property_, value in style.get_css_properties():
                properties[property_] = value

            if self.verbose > 1:
                print('StylesheetGenerator:', 'final properties:  ', properties)

            self.selectors[selector] = properties

    def get_stylesheet(self):
        csstxt = ''

        for selector in sorted(self.selectors, key=_key_selector):
            properties = self.selectors[selector]
            csstxt += f'{selector} {{\n'
            for property_, value in sorted(properties.items()):
                csstxt += f'  {property_}: {value};\n'
            csstxt += '}\n\n'

        return csstxt


# https://blogboard.io/blog/knowledge/python-sorted-lambda/
def _key_selector(selector):
    if selector.startswith('h'):
        return (0, selector)

    if selector == 'p':
        return (10, selector)

    if selector.startswith('.'):
        return (1000, selector)

    return (100, selector)
