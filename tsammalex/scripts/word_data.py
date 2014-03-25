# coding: utf8
from __future__ import unicode_literals
import re
from collections import defaultdict

from clld.scripts.util import parsed_args
from clld.db.meta import DBSession
from clld.db.models.common import Value

from tsammalex.models import Word


def parens(c, p=None):
    p = p or ('\(', '\)')
    return p[0] + '(?P<c>' + c + ')' + p[1]


nc_atom = '\s*n?[0-9]{1}\s*i*\??\s*'
nc_pair = nc_atom + '(~' + nc_atom + ')*'
memadi_atom = '(me|ma|di|b.)\-?'
dialect_atom = "(W|N|E|C|S|D|Hm|ǂA)"

PATTERNS = [
    ('grammar', 'm|n|f', None),
    ('variety', dialect_atom + '(\s*,\s*' + dialect_atom + ')*', None),
    ('grammar', nc_pair + '(/' + nc_pair + ')*', None),
    ('grammar', memadi_atom + '(\s*,\ş*' + memadi_atom + ')*', None),
    ('grammar', 'ha(/hi)?', None),
    ('phonetic', '[^0-9][^\]]*', ('\[', '\]')),
    ('ref', '[0-9]+', ('\[', '\]')),
]
PATTERNS = [(k, re.compile(parens(c, p))) for k, c, p in PATTERNS]


def split_words(s):
    s = re.sub('\s+', ' ', s)
    chunk = ''
    in_bracket = False

    for c in s:
        if c in ['(', '[']:
            in_bracket = True
        if c in [')', ']']:
            in_bracket = False
        if c in [',', ';'] and not in_bracket:
            yield chunk
            chunk = ''
        else:
            chunk += c
    if chunk:
        yield chunk

    #ref = re.compile('\[(?P<refid>[0-9]+)\]$')
    #    m = ref.search(word.strip())
    #    if m:
    #        yield (word[:m.start()].strip(), int(m.group('refid')) - 1)
    #    else:
    #        yield (word.strip(), None)


def parsed_word(words, i, fp):
    word = words[i]
    desc = None
    classes = defaultdict(list)

    if ':' in word:
        # remove genus, if present.
        word = word.split(':', 1)[1]

    n = word.strip()
    for k, p in PATTERNS:
        for m in p.finditer(n):
            classes[k].append(m.group('c'))
        n = p.sub('', n)
    n = n.strip()
    if n.endswith("'"):
        parts = n.split("'")
        desc = parts[-2].strip()
        n = "'".join(parts[:-2])
    if '(' in n or '[' in n or re.search("\s+'", n):
        print word, '-----', n
        fp.write(('%s\t%s\t%s\n' % (word, n, n)).encode('utf8'))

    return (
        Word(
            name=n,
            description=desc,
            phonetic=', '.join(classes['phonetic']) or None,
            grammatical_info=', '.join(classes['grammar']) or None),
        classes['ref'],
        classes['variety'])


def parsed_words(words, fp):
    words = list(split_words(words))
    return [parsed_word(words, i, fp) for i in range(len(words))]


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
