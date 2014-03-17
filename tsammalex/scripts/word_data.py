# coding: utf8
from __future__ import unicode_literals
import re

from clld.scripts.util import parsed_args
from clld.db.meta import DBSession
from clld.db.models.common import Value


parens = lambda c: '\((?P<c>' + c + ')\)'


nc_atom = '\s*n?[0-9]{1}\s*i*\??\s*'
nc_pair = nc_atom + '(~' + nc_atom + ')*'
memadi_atom = '(me|ma|di|bó)\-?'

PATTERNS = {
    'genus': 'm|n|f',
    'caps': '([A-Z]{1}|Hm)(,\s*([A-Z]{1}|Hm))*',
    'nclass': nc_pair + '(/' + nc_pair + ')*',
    'memadi': memadi_atom + '(,\ş*' + memadi_atom + ')*',
    'hahi': 'ha(/hi)?',
}

for k in PATTERNS:
    PATTERNS[k] = re.compile(parens(PATTERNS[k]))


def parsed_word(word):
    desc = None
    classes = {}

    n = word.strip()
    if '(' in n:
        for k, p in PATTERNS.items():
            m = p.search(n)
            if m:
                classes[k] = m.group('c')
                n = p.sub('', n, 1)
    n = n.strip()
    if n.endswith("'"):
        parts = n.split("'")
        desc = parts[-2].strip()
        n = "'".join(parts[:-2])
    return n, desc, classes


def main(args):
    # TODO: split off 'genus:', get translations for genus!
    u = 0
    for i, v in enumerate(DBSession.query(Value)):
        n = v.name.strip()
        if '(' in n:
            for _, p in PATTERNS.items():
                n = p.sub('', n)
            if '(' in n:
                #print n
                u += 1
        n = n.strip()
        if n.endswith("'"):
            parts = n.split("'")
            print n, '--->', parts[-2]
    print u, 'of', i, 'stuff in (...) unmatched'


if __name__ == '__main__':
    main(parsed_args())
