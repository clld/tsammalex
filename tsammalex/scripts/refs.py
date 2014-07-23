from __future__ import print_function
import re

from clld.util import slug


KEY_MAP = {
    'dickesn1994': 'dickens1994',
    'duplessised2005': 'duplessis2005',
    'eksteened1997': 'eksteen1997',
    'snymanetal1990': 'snymaned1990',
    'trail1994': 'traill1994',
    'triall1994': 'traill1994',
    'vanrooyened2001': 'vanrooyen2001',
    'vanrooyenetal2001': 'vanrooyen2001',
}

YEAR_PAGES = re.compile('(?P<year>[0-9]{4})(:(?P<pages>[0-9]+[,\s/\-0-9]*))?$')
SEP = re.compile(r'(?:[^,(]|\([^)]*\))+')


def get_refs(line):
    line = line.strip()\
        .replace('|Wikipedia', '')\
        .replace(',|', ',')\
        .replace(' (ed.)', ' ed.')\
        .replace(':,77', ':77,')
    if '(' in line and ')' not in line:
        line = line + ')'
    for piece in SEP.findall(line):
        piece = piece.strip()
        if piece.startswith('http://'):
            # TODO: handle URL
            yield piece
            continue
        if not ('(' in piece and ')' in piece):
            if 'dobes' in piece.lower():
                yield 'DOBES'
            elif piece == 'Cunningham ed.':
                yield ('cunningham', None)
            else:
                print(piece)
                raise ValueError
            continue
        assert len(piece.split('(')) == 2

        pages = None
        year_pages = piece.split('(')[1].split(')')[0]
        m = YEAR_PAGES.match(year_pages)
        if not m:
            if year_pages == '?:15':
                pages = '15'
            assert year_pages in ['?:15', '1994:']
        else:
            pages = m.group('pages')
        if ':' in piece:
            r = piece.split(':')[0]
        else:
            r = piece.split(')')[0]
        r = slug(r)
        r = KEY_MAP.get(r, r)
        yield (r, pages)


if __name__ == '__main__':
    refs = {}
    for line in open('refs.txt'):
        refs[line.strip()] = list(get_refs(line))

    for k, v in refs.items():
        print(k)
        print(v)
