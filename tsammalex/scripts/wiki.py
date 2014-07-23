# coding: utf8
# pragma: no cover
import json
from base64 import urlsafe_b64encode

import requests
from bs4 import BeautifulSoup, NavigableString
from purl import URL

from clld.lib import bibtex


def get_refs(args):
    return bibtex.Database.from_file(args.data_file('wiki', 'refs.bib'))


def text(n):
    if isinstance(n, (NavigableString, unicode)):
        return ('%s' % n).strip()
    return ' '.join(list(n.stripped_strings)).strip()


def split(s, sep=','):
    return [ss.strip() for ss in s.split(sep)]


def get_data(args, name, type_, url, get_result):
    fpath = args.data_file('wiki', type_, urlsafe_b64encode(name))
    if not fpath.exists():
        res = get_result(requests.get(url))
        with open(fpath, 'w') as fp:
            json.dump(res, fp)
    else:
        with open(fpath) as fp:
            res = json.load(fp)
    return res


def get_eol(args, name):
    """
    http://eol.org/api/search/1.0.json?q=Panthera+leo&page=1&exact=true&\
    filter_by_taxon_concept_id=&filter_by_hierarchy_entry_id=&filter_by_string=
    """
    url = URL('http://eol.org/api/search/1.0.json?page=1&exact=true')

    def get_result(res):
        res = res.json().get('results')
        return res[0] if res else {}

    return get_data(args, name, 'eol', url.query_param('q', name), get_result)


def get_wikipedia(args, name):
    url = URL(
        "http://en.wikipedia.org/w/api.php?format=json&action=query&prop=info&inprop=url")

    def get_result(res):
        """
{
    "query": {
        "pages": {
            "45724": {
                "contentmodel": "wikitext",
                "counter": "",
                "editurl":
                    "http://en.wikipedia.org/w/index.php?title=Panthera_leo&action=edit",
                "fullurl": "http://en.wikipedia.org/wiki/Panthera_leo",
                "lastrevid": 535861485,
                "length": 71,
                "ns": 0,
                "pageid": 45724,
                "pagelanguage": "en",
                "redirect": "",
                "title": "Panthera leo",
                "touched": "2014-02-27T02:04:39Z"
            }
        }
    }
}
        """
        res = res.json().get('query', {}).get('pages', {})
        return res.values()[0] if res else {}

    return get_data(args, name, 'wikipedia', url.query_param('titles', name), get_result)


def get(args, path, html=True):
    if html:
        fpath = args.data_file('wiki', urlsafe_b64encode(path))
    else:
        fpath = args.data_file('wiki', 'images', urlsafe_b64encode(path))
    if not fpath.exists():
        content = requests.get(
            "https://lingweb.eva.mpg.de" + path, verify=False).content
        with open(fpath, 'w') as fp:
            fp.write(content)
    else:
        with open(fpath) as fp:
            content = fp.read()
    if html:
        return BeautifulSoup(content)
    else:
        return content
