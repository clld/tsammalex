"""
"""
from __future__ import print_function, unicode_literals, absolute_import, division
import json

from bs4 import BeautifulSoup as bs
import requests
from purl import URL

from clld.scripts.util import parsed_args

from clld.db.meta import DBSession

from tsammalex.models import Species

"""
<h1 class='scientific_name'>
<i>Acacia fleckii</i>
<span class='assistive'> &amp;mdash; Overview</span>
</h1>
<h2 title='Preferred common name for this taxon.'>
Blade Thorn
"""


def eol_api(name, id=None, **kw):
    path = '1.0'
    if name != 'search':
        path += '/%s' % id
    url = URL('http://eol.org/api/%s/%s.json' % (name, path)).query_params(kw)
    try:
        return requests.get(url).json()
    except ValueError:
        print(name, id)
        return {}


def get_eol_id(name):
    res = eol_api('search', q=name, page=1, exact='false')
    if res.get('results'):
        return res['results'][0]['id']


def eol(id):
    kw = dict(
        images=0,
        videos=0,
        sounds=0,
        maps=0,
        text=0,
        iucn='true',
        subjects='overview',
        licenses='all',
        details='true',
        common_names='true',
        synonyms='false',
        references='true',
        vetted=0)
    data = eol_api('pages', id, **kw)
    if isinstance(data, list):
        print(data)
        return {}
    if data.get('taxonConcepts'):
        for tc in data['taxonConcepts']:
            if tc['nameAccordingTo'].startswith('Species 2000'):
                break
        else:
            tc = data['taxonConcepts'][0]
        taxonomy = eol_api('hierarchy_entries', tc['identifier'])
        data.update(ancestors=taxonomy['ancestors'])
    return data


def main(args):
    res = {}
    for species in DBSession.query(Species):
        res[species.id] = {'eol': {}, 'wikipedia': {}}
        if not species.eol_id:
            species.eol_id = get_eol_id(species.name)
        if species.eol_id:
            res[species.id]['eol'] = eol(species.eol_id)
            if res[species.id]['eol']:
                continue

        if species.name.endswith(' sp.'):
            species.wikipedia_url = species.wikipedia_url[:-2]
        r = requests.get(species.wikipedia_url)
        if r.status_code == 404:
            print(species.id)
            continue
        html = bs(r.text)
        c = {}
        for tr in html.find_all('tr'):
            tds = list(tr.find_all('td'))
            if len(tds) != 2:
                continue
            for level in 'Kingdom Phylum Class Order Family Genus'.split():
                if tds[0].text == level + ':':
                    try:
                        c[level.lower()] = tds[1].find('span').find('a').text
                    except:
                        try:
                            c[level.lower()] = tds[1].find('span').find('i').find('b').text
                        except:
                            try:
                                c[level.lower()] = tds[1].find('a').text
                            except:
                                print(tds[1])
        if not c:
            print(species.id)
        else:
            res[species.id]['wikipedia'] = c

    with open(args.data_file('classification.json'), 'w') as fp:
        json.dump(res, fp)


if __name__ == '__main__':
    main(parsed_args())
