"""Utility script to extract the text abstract of Wikipedia from DBpedia

The unquote method is taken from rdflib (c) Sean B. Palmer, inamidst.com
and distributed under the GPL 2, W3C, BSD, or MIT licenses :
https://code.google.com/p/rdflib/source/browse/rdflib/plugins/parsers/ntriples.py

The rest of the script is distributed under the BSD or MIT licenses as well.
"""

uriref = b(r'<([^:]+:[^\s"<>]+)>')
literal = b(r'"([^"\\]*(?:\\.[^"\\]*)*)"')
litinfo = b(r'(?:@([a-z]+(?:-[a-z0-9]+)*)|\^\^') + uriref + b(r')?')

r_line = re.compile(b(r'([^\r\n]*)(?:\r\n|\r|\n)'))
r_wspace = re.compile(b(r'[ \t]*'))
r_wspaces = re.compile(b(r'[ \t]+'))
r_tail = re.compile(b(r'[ \t]*\.[ \t]*'))
r_uriref = re.compile(uriref)
r_nodeid = re.compile(b(r'_:([A-Za-z][A-Za-z0-9]*)'))
r_literal = re.compile(literal + litinfo)

bufsiz = 2048
validate = False

class Node(unicode): pass

class ParseError(Exception): pass

class Sink(object):
    def __init__(self):
        self.length = 0

    def triple(self, s, p, o):
        self.length += 1
        print (s, p, o)

quot = {b('t'): u'\t', b('n'): u'\n', b('r'): u'\r', b('"'): u'"', b('\\'): u'\\'}
r_safe = re.compile(b(r'([\x20\x21\x23-\x5B\x5D-\x7E]+)'))
r_quot = re.compile(b(r'\\(t|n|r|"|\\)'))
r_uniquot = re.compile(b(r'\\u([0-9A-F]{4})|\\U([0-9A-F]{8})'))


def unquote(s):
    """Unquote an N-Triples string."""
    if not validate:
        return s.decode('unicode-escape')
    else:
        result = []
        while s:
            m = r_safe.match(s)
            if m:
                s = s[m.end():]
                result.append(m.group(1).decode('ascii'))
                continue

            m = r_quot.match(s)
            if m:
                s = s[2:]
                result.append(quot[m.group(1)])
                continue

            m = r_uniquot.match(s)
            if m:
                s = s[m.end():]
                u, U = m.groups()
                codepoint = int(u or U, 16)
                if codepoint > 0x10FFFF:
                    raise ParseError("Disallowed codepoint: %08X" % codepoint)
                result.append(unichr(codepoint))
            elif s.startswith(b('\\')):
                raise ParseError("Illegal escape at: %s..." % s[:10])
            else: raise ParseError("Illegal literal character: %r" % s[0])
        return u''.join(result)

        result = []
        while s:
            m = r_safe.match(s)
            if m:
                s = s[m.end():]
                result.append(m.group(1).decode('ascii'))
                continue

            m = r_quot.match(s)
            if m:
                s = s[2:]
                result.append(quot[m.group(1)])
                continue

            m = r_uniquot.match(s)
            if m:
                s = s[m.end():]
                u, U = m.groups()
                codepoint = int(u or U, 16)
                if codepoint > 0x10FFFF:
                    raise ParseError("Disallowed codepoint: %08X" % codepoint)
                result.append(unichr(codepoint))
            elif s.startswith(b('\\')):
                raise ParseError("Illegal escape at: %s..." % s[:10])
            else: raise ParseError("Illegal literal character: %r" % s[0])
        return u''.join(result)
