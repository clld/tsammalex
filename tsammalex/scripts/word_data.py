# coding: utf8
# pragma: no cover
from __future__ import unicode_literals, print_function, absolute_import, division
import re
from itertools import chain
from collections import defaultdict

from clld.scripts.util import parsed_args
from clld.db.meta import DBSession
from clld.db.models.common import Value
from clld.util import nfilter

from tsammalex.models import Word


def parens(c, p=None):
    p = p or ('\(', '\)')
    return p[0] + '(?P<c>' + c + ')' + p[1]


nc_atom = '\s*n?[0-9]{1}\s*i*\??\s*'
nc_pair = nc_atom + '(~' + nc_atom + ')*'
memadi_atom = '(ka|me|ma|di|b.)\-?'
dialect_atom = "(W|N|E|C|S|D|Hm|ǂA)"

PATTERNS = [
    ('grammar', 'm|n|f', None),
    ('variety', dialect_atom + '(\s*,\s*' + dialect_atom + ')*', None),
    ('grammar', nc_pair + '(/(' + nc_pair + '|\?))*', None),
    ('grammar', memadi_atom + '(\s*,\ş*' + memadi_atom + ')*', None),
    ('grammar', 'ha(/hi)?', None),
    ('phonetic', '[^0-9][^\]]*', ('\[', '\]')),
    ('ref', '[0-9]+', ('\[', '\]')),
]
PATTERNS = [(k, re.compile(parens(c, p))) for k, c, p in PATTERNS]


def split_words(s):
    """
    split string at , or ; if this is not within brackets.
    """
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


def parsed_word(words, i, fp, lang):
    word = words[i]
    if word == "cf. phágê (di-) 'black-footed cat' (Felis nigripes) [8]":
        return

    desc = None
    comment = None
    classes = defaultdict(list)

    if ':' in word:
        # remove genus, if present.
        word = word.split(':', 1)[1]

    n = word.strip()

    for s, t in [
        ('?', 'unknown'),
        ('dim.', 'diminutive'),
        ('and tonal variants', 'and tonal variants'),
        ('Schmetterlinge', 'Schmetterling'),
        ('fruit', 'fruit'),
        ("cf. jao, jaqo, ǃoo 'hole'", "cf. jao, jaqo, ǃoo 'hole'"),
    ]:
        s = '(' + s + ')'
        if s in n:
            n = n.replace(s, '').strip()
            comment = t

    n = n.replace('(koggelmander)', "koggelmander 'agama'")

    for s, t in [
        ("ǀháí (1/1~4?) 'rhino", "ǀháí (1/1~4?) 'rhino'"),
        ("(katlagter)", "katlagter 'babbler'"),
        ("nǃùqù (1/4) (S) 'hare", "nǃùqù (1/4) (S) 'hare'"),
        ("modíoló (me-) 'bush hare", "modíoló (me-) 'bush hare'"),
        ("(padda)", "padda 'frog, toad'"),
    ]:
        n = n.replace(s, t)

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
        if lang != 'Setswana':
            print(word, '-----', n)
        fp.write(('%s\t%s\t%s\n' % (word, n, n)).encode('utf8'))

    if lang != 'Taa':
        return [(
            Word(
                name=n,
                comment=comment,
                description=desc,
                phonetic=', '.join(classes['phonetic']) or None,
                grammatical_info=', '.join(classes['grammar']) or None),
            classes['ref'],
            classes['variety'])]

    if classes['variety']:
        assert len(classes['variety']) == 1
        varieties = [_s.strip() for _s in classes['variety'][0].split(',')]
    else:
        varieties = []
    if varieties:
        return [(
            Word(
                name=n,
                comment=comment,
                description=desc,
                phonetic=', '.join(classes['phonetic']) or None,
                grammatical_info=', '.join(classes['grammar']) or None),
            classes['ref'],
            [v]
        ) for v in varieties]
    return [(
        Word(
            name=n,
            comment=comment,
            description=desc,
            phonetic=', '.join(classes['phonetic']) or None,
            grammatical_info=', '.join(classes['grammar']) or None),
        classes['ref'],
        [])]


def parsed_words(words, fp, lang):
    for s, t in [
        ("nǁá(q)'ám", "nǁáq'ám, nǁá'ám"),
        ("ǀga̋é.b/(s)", "ǀga̋é.b, ǀga̋é.s"),
        ("ǀkhóò.b/(s)", "ǀkhóò.b, ǀkhóò.s"),
        ("nǂúq(y)è", "nǂúqyè, nǂúqè"),
        ("ǀ'hùī (n̏ǀ'hùīn)", "ǀ'hùī, n̏ǀ'hùīn"),
        ("sùr(ù)tsi̋ǃgùűbȅ.s", "sùr(ù)tsi̋ǃgùűbȅ.s, sùrùtsi̋ǃgùűbȅ.s"),
        ("dàqhńn(tê)", "dàqhńn, dàqhńntê"),
        ("ǀàālè (ǀàlé)", "ǀàālè, ǀàlé"),
        ("ǁúq(l)è", "ǁúqlè, ǁúqè"),
        ("nǃhȁè (nǃȁhè)", "nǃhȁè, nǃȁhè"),
        ("(ǀxòo) tsàhnà", "ǀxòo tsàhnà, tsàhnà"),
        ("(kú-)ǃáná", "kúǃáná, ǃáná"),
        ("ǀgài̋o.b(/s)", "ǀgài̋o.b, ǀgài̋o.s"),
        ("dz(h)òhè", "dzhòhè, dzòhè, dzhòè (?)"),
        ("ǀqx'á(y)è", "ǀqx'áyè, ǀqx'áè"),
    ]:
        words = words.replace(s, t)
    words = list(split_words(words))
    return nfilter(chain(*[parsed_word(words, i, fp, lang) for i in range(len(words))]))


def main(args):
    u = 0
    for i, v in enumerate(DBSession.query(Value)):
        n = v.name.strip()
        if '(' in n:
            for _, p in PATTERNS.items():
                n = p.sub('', n)
            if '(' in n:
                u += 1
        n = n.strip()
        if n.endswith("'"):
            parts = n.split("'")
            print(n, '--->', parts[-2])
    print(u, 'of', i, 'stuff in (...) unmatched')


if __name__ == '__main__':
    main(parsed_args())
