# coding: utf8
import json
import re
from base64 import urlsafe_b64decode, urlsafe_b64encode

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


def split_words(s):
    r = re.compile(r'(?:[^,(]|\([^)]*\))+')
    ref = re.compile('\[(?P<refid>[0-9]+)\]$')
    for word in r.findall(s):
        m = ref.search(word.strip())
        if m:
            yield (word[:m.start()].strip(), int(m.group('refid')) - 1)
        else:
            yield (word.strip(), None)


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
    http://eol.org/api/search/1.0.json?q=Panthera+leo&page=1&exact=true&filter_by_taxon_concept_id=&filter_by_hierarchy_entry_id=&filter_by_string=
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
                "editurl": "http://en.wikipedia.org/w/index.php?title=Panthera_leo&action=edit",
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


LICENSE_URL_MAP = {
    'http://creativecommons.org/licenses/by-sa/2.0/de/legalcode':
    'http://creativecommons.org/licenses/by-sa/2.0/de/deed.en',
    'http://en.wikipedia.org/wiki/http://en.wikipedia.org/wiki/Public_domain':
    'http://en.wikipedia.org/wiki/Public_domain',
}

LICENSE_NAME_MAP = {
    u'Creative Commons Attribution-Share Alike 3.0 Unported':
        'http://creativecommons.org/licenses/by-sa/3.0/deed.en',
}

LICENSES = dict([
    ('http://creativecommons.org/licenses/by/2.0/', u'Creative Commons Attribution 2.0 License'),
    ('http://creativecommons.org/licenses/by/2.0/deed.en', u'Creative Commons Attribution 2.0 Generic'),
    ('http://creativecommons.org/licenses/by/3.0/deed.en', u'Creative Commons Attribution 3.0 Unported'),
    ('http://creativecommons.org/licenses/by-sa/2.0/de/deed.en', u'Creative Commons Attribution-Share Alike 2.0 Germany'),
    ('http://creativecommons.org/licenses/by-sa/2.0/', u'Creative Commons Attribution ShareAlike 2.0'),
    ('http://creativecommons.org/licenses/by-sa/2.0/deed.en', u'Creative Commons Attribution-Share Alike 2.0 Generic'),
    ('http://creativecommons.org/licenses/by-sa/2.5/deed.en', u'Creative Commons Attribution-Share Alike 2.5 Generic'),
    ('http://creativecommons.org/licenses/by-sa/2.5/', u'Creative Commons Attribution ShareAlike 2.5'),
    ('http://creativecommons.org/licenses/by-sa/3.0/', u'Creative Commons Attribution-ShareAlike 3.0'),
    ('http://creativecommons.org/licenses/by-sa/3.0/deed.en', u'Creative Commons Attribution-ShareAlike 3.0 Unported'),
    ('http://en.wikipedia.org/wiki/Public_domain', u'public domain'),
    ('http://commons.wikimedia.org/wiki/GNU_Free_Documentation_License', u'GNU Free Documentation License'),
])


def get_img(args, gb):
    """
<div class="fullImageLink" id="file">
    <a href="/tsammalex/images/e/ef/LepusSaxatilis01T.JPG">
        <img alt="File:LepusSaxatilis01T.JPG" src="/tsammalex/images/e/ef/LepusSaxatilis01T.JPG" width="300" height="177" />
    </a><br /><small>No higher resolution available.</small><br />
    <a href="/tsammalex/images/e/ef/LepusSaxatilis01T.JPG">LepusSaxatilis01T.JPG</a>‎ (300 × 177 pixels, file size: 41 KB, MIME type: image/jpeg)</div>
<hr />
<table class="wikitable" cellpadding="3">
<tr>
<td> <i>Name</i> </td><td> <a href="/tsammalex/index.php/Lepus_saxatilis" title="Lepus saxatilis">Lepus saxatilis</a>
</td></tr>
<tr>
<td> <i>Source</i> </td><td> <a href="http://en.wikipedia.org/wiki/Main_Page" class="external text" rel="nofollow">en.wikipedia</a> (original), <a href="http://commons.wikimedia.org/wiki/Main_Page" class="external text" rel="nofollow">Wikipedia Commons</a>
</td></tr>
<tr>
<td> <i>Date</i> </td><td> 2007-07-27 (original upload date to en.wikipedia)
</td></tr>
<tr>
<td> <i>Place</i> </td><td> Ngorongoro Crater, Tanzania
</td></tr>
<tr>
<td> <i>Author</i> </td><td> Lee R. Berger, uploaded by <a href="http://en.wikipedia.org/wiki/User:Profberger" class="external text" rel="nofollow">Profberger</a> at en.wikipedia
</td></tr>
<tr>
<td> <i>Permission</i> </td><td> CC-BY-2.5; Released under the <a href="http://commons.wikimedia.org/wiki/GNU_Free_Documentation_License" class="external text" rel="nofollow">GNU Free Documentation License</a>
</td></tr>
<tr>
<td> <i>Comments</i> </td><td>
</td></tr>
<tr>
<td> <i>Keywords</i> </td><td>
</td></tr>
</table>
    """
    def imgdata(img):
        get(args, img['src'], html=False)
        return dict(
            src=img['src'], width=img['width'], height=img['height'])

    def license(td):
        l = {}
        for child in td.children:
            if isinstance(child, (NavigableString, unicode)):
                child = unicode(child)
                if not child.startswith('This file is licensed under'):
                    l['comment'] = child
            else:
                assert child.name == 'a'
                url = LICENSE_URL_MAP.get(child['href'], child['href'])
                if url not in LICENSES:
                    url = LICENSE_NAME_MAP.get(child.string, child['href'])
                if url not in LICENSES:
                    print 'license url: ---', url
                    l['license'] = (url, child.string)
                else:
                    l['license'] = (url, LICENSES[url])
        return l

    res = {'metadata': {}}
    # there are two image links within a gallerybox!
    small = gb.find('a', class_='image')
    large = gb.find('div', class_='gallerytext').find('a')

    if small:
        thumbnail = small.find('img')
        if thumbnail:
            res['thumbnail'] = imgdata(thumbnail)

    for name, a in [('small', small), ('large', large)]:
        if not a:
            continue
        bs = get(args, a['href'])
        full = bs.find('div', id='file')
        if not full:
            continue
        res[name] = imgdata(full.find('img'))
        md = bs.find('table', class_='wikitable', cellpadding='3')
        if not md:
            continue
        for tr in md.find_all('tr'):
            key, value = list(tr.find_all('td'))
            key = text(key).lower()
            if key == 'name':
                continue
            if key in ['author', 'date', 'place', 'comments', 'keywords']:
                value = text(value)
            elif key == 'permission':
                try:
                    value = license(value)
                except:
                    print a['href']
                    raise
            else:
                value = unicode(value).replace('<td>', '').replace('</td>', '').strip()
            if key and value:
                res['metadata'][key] = value
    return res


class Species(object):
    def __init__(self, name):
        self.name = name
        self.family = None
        self.genus = None
        self.other_data = {}
        self.categories = []
        self.names = {}
        self.images = []
        self.countries = []
        self.ecoregions = []
        self.references = []
        self.eol = {}
        self.wikipedia = {}

    def json(self):
        return {k: getattr(self, k) for k in 'name description genus family categories names images countries ecoregions references eol wikipedia other_data'.split()}


def parse_species(args, bs):
    """
<h1 id="firstHeading" class="firstHeading">Juliformia sp.</h1>
	<div id="bodyContent">
<p><font size="5">Worm-like millipedes</font><br /><br />
<font size="3">Order Spirobolida?</font> <br /><br /><br />
</p><p><font size="4">Names</font>
</p>

<table border="2" cellpadding="3">

<tr>
<td><font size="3"><i>Afrikaans</i></td><td><font size="3">duisendpoot <sup id="cite_ref-0" class="reference"><a href="#cite_note-0">[1]</a></sup>
</td></tr>
<tr>
<td><font size="3"><i>Deutsch</i></td><td><font size="3">
</td></tr>
<tr>
<td><font size="3"><i>Gǀui</i></td><td><font size="3">
</td></tr>
<tr>
<td><font size="3"><i>Juǀ'hoansi</i></td><td><font size="3">
</td></tr>
<tr>
</td></tr>
<tr>

</td></tr>
</table>
<p><br />
<font size="4">Distribution</font>
</p>
<table cellpadding="3">
<tr>
<td><i>Countries</i> </td><td> Botswana, Namibia
</td></tr>
<tr>
<td><i>Ecoregions</i> </td><td> AT1309 Kalahari xeric savanna
</td></tr></table>
<p><br />
<font size="4">Description</font> <br />
<br /><br />
<br />
<font size="4">Uses</font> <br />
<br /><br />
<br />
<font size="4">Comments</font> <br />
order "Juliformia"?<br /><br />
<br />
<font size="4">Short references</font>  (Cf. <a href="/tsammalex/index.php/References" title="References">References</a>) <br />
Carruthers ed. (2000:13), <a href="http://en.wikipedia.org/wiki/Spirobolida" class="external text" rel="nofollow">Wikipedia</a><br />
</p>
<ol class="references"><li id="cite_note-0"><a href="#cite_ref-0">↑</a>  Eksteen ed. (1997:1120)</li></ol><br />
<p><br />
<font size="4">Gallery</font> <br />
</p>
<table class="gallery" cellspacing="0" cellpadding="0">
	<tr>
		<td><div class="gallerybox" style="width: 155px;">
			<div class="thumb" style="padding: 28px 0; width: 150px;">
			    <div style="margin-left: auto; margin-right: auto; width: 120px;">
			        <a href="/tsammalex/index.php/File:Juliformia01T.JPG" class="image">
			            <img alt="" src="/tsammalex/images/thumb/8/8c/Juliformia01T.JPG/120px-Juliformia01T.JPG" width="120" height="90" /></a></div></div>
			<div class="gallerytext">
<p><a href="/tsammalex/index.php/File:Juliformia01.JPG" title="File:Juliformia01.JPG">Large</a>
</p>
			</div>
		</div></td>
		<td><div class="gallerybox" style="width: 155px;">
			<div class="thumb" style="padding: 28px 0; width: 150px;"><div style="margin-left: auto; margin-right: auto; width: 120px;"><a href="/tsammalex/index.php/File:Juliformia02T.JPG" class="image"><img alt="" src="/tsammalex/images/thumb/4/40/Juliformia02T.JPG/120px-Juliformia02T.JPG" width="120" height="90" /></a></div></div>
			<div class="gallerytext">
<p><a href="/tsammalex/index.php/File:Juliformia02.JPG" title="File:Juliformia02.JPG">Large</a>
</p>
			</div>
		</div></td>
		<td><div class="gallerybox" style="width: 155px;">
			<div class="thumb" style="padding: 28px 0; width: 150px;"><div style="margin-left: auto; margin-right: auto; width: 120px;"><a href="/tsammalex/index.php/File:Juliformia03T.JPG" class="image"><img alt="" src="/tsammalex/images/thumb/9/97/Juliformia03T.JPG/120px-Juliformia03T.JPG" width="120" height="90" /></a></div></div>
			<div class="gallerytext">
<p><a href="/tsammalex/index.php/File:Juliformia03.JPG" title="File:Juliformia03.JPG">Large</a>
</p>
			</div>
		</div></td>
	</tr>
</table>
    """
    def parse_pseudo_dl(p):
        res = {}
        key = None
        values = []
        for child in p.children:
            if child.name == 'br':
                continue
            if child.name == 'font' and child['size'] == '4':
                if key and values:
                    res[key] = values
                key = child.string
                values = []
            elif child.name == 'a':
                values.append((child['href'], child.string))
            else:
                t = text(child)
                if t:
                    values.append(t)
        #if res:
        #    print res
        return res

    tables = list(bs.find_all('table'))
    if not tables:
        return

    species = Species(bs.find('h1').string)

    for i, p in enumerate(bs.find_all('p')):
        if i == 0:
            species.description = text(p.find('font', size='5'))
            if species.description and ':' in species.description:
                genus, desc = species.description.split(':', 1)
                species.genus = genus.strip()
                species.description = desc.strip()
            species.family = text(p.find('font', size='3'))
        else:
            species.other_data.update(parse_pseudo_dl(p))

    olrefs = bs.find('ol', class_='references')
    if olrefs:
        for li in olrefs.find_all('li'):
            refs = []
            for child in li:
                if getattr(child, 'name', None) == 'a':
                    if child['href'].startswith('#'):
                        continue
                    refs.append(child['href'])
                else:
                    if text(child):
                        refs.append(text(child))
            #if len(refs) > 1:
            #    print refs
            if refs:
                species.references.append('|'.join(refs))
                #print ('|'.join(refs)).encode('utf8')

    for tr in tables[0].find_all('tr'):
        lang, words = map(text, list(tr.find_all('td')))
        if words:
            species.names[lang] = list(split_words(words))

    for tr in tables[1].find_all('tr'):
        tds = list(tr.find_all('td'))
        if tds[0].find('i').string == 'Countries':
            species.countries = [t for t in split(text(tds[1])) if t != 'undefined_country']

        if tds[0].find('i').string == 'Ecoregions':
            species.ecoregions = [t for t in split(text(tds[1])) if t != 'undefined']

    gallery = bs.find('table', class_='gallery')
    if gallery:
        for div in gallery.find_all('div', class_='gallerybox'):
            species.images.append(get_img(args, div))

    return species


def get_species(args, a, species):
    cat_path = a['href']
    cat_name = a.string
    div = get(args, cat_path).find('div', id='mw-pages')
    if not div:
        print 'no div mw-pages ---', cat_path
        return False
    for ul in div.find_all('ul'):
        for a in ul.find_all('a'):
            res = parse_species(args, get(args, a['href']))
            if res:
                if res.name not in species:
                    res.eol = get_eol(args, res.name)
                    res.wikipedia = get_wikipedia(args, res.name)
                    species[res.name] = res
                species[res.name].categories.append(cat_name)
    return True


def get_categories(args):
    species = {}
    ul = get(args, "/tsammalex/index.php?title=Special:Categories&limit=250").find('ul')
    for a in ul.find_all('a'):
        get_species(args, a, species)
    with open(args.data_file('species.json'), 'w') as fp:
        json.dump({k: v.json() for k, v in species.items()}, fp)
    ps = {}
    with open('refs.txt', 'w') as fp:
        for s in species.values():
            for i in s.images:
                if 'permission' in i['metadata']:
                    ps[i['metadata']['permission'].get('license')] = 1
            for ref in s.references:
                fp.write(('%s\n' % ref).encode('utf8'))
    for k in ps.keys():
        print k
