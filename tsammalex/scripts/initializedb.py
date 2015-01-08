# coding: utf8
# pragma: no cover
from __future__ import unicode_literals, division, absolute_import, print_function
import sys
import json
from itertools import groupby
from functools import partial
import re

from purl import URL
from path import path
from sqlalchemy.orm import joinedload
from clld.scripts.util import (
    initializedb, Data, bibtex2source, glottocodes_by_isocode, add_language_codes,
    ExistingDir,
)
from clld.db.meta import DBSession
from clld.db.models import common
from clld.lib.dsv import reader
from clld.lib.bibtex import Database
from clld.util import nfilter, jsonload

from tsammalex import models
from tsammalex.scripts.util import (
    update_species_data, load_ecoregions, from_csv, load_countries, data_files,
    get_gbif_id,
)


def main(args):
    def data_file(*comps): 
        return path(args.data_repos).joinpath('tsammalexdata', 'data', *comps)

    data = Data()
    data.add(common.Dataset, 'tsammalex',
        id="tsammalex",
        name="Tsammalex",
        description="A lexical database on plants and animals",
        publisher_name="Max Planck Institute for Evolutionary Anthropology",
        publisher_place="Leipzig",
        publisher_url="http://www.eva.mpg.de",
        domain='tsammalex.clld.org',
        license='http://creativecommons.org/licenses/by/4.0/',
        contact='naumann@eva.mpg.de',
        jsondata={
            'license_icon': 'cc-by.png',
            'license_name': 'Creative Commons Attribution 4.0 International License'})
    data.add(common.Contribution, 'tsammalex', name="Tsammalex", id="tsammalex")
    glottolog = glottocodes_by_isocode('postgresql://robert@/glottolog3')

    for rec in Database.from_file(data_file('sources.bib')):
        data.add(models.Bibrec, rec.id, _obj=bibtex2source(rec, cls=models.Bibrec))

    load_ecoregions(data_file, data)
    load_countries(data)

    def languoid_visitor(lang, row, _):
        add_language_codes(
            data, lang, lang.id.split('-')[0], glottolog, glottocode=row[-1] or None)
        if lang.id == 'eng':
            lang.is_english = True

    def habitat_visitor(cat, *_):
        cat.is_habitat = True

    def species_visitor(eol, species, *_):
        species.gbif_id = get_gbif_id(data_file, species.id)
        species.countries_str = ' '.join([e.id for e in species.countries])
        species.ecoregions_str = ' '.join([e.id for e in species.ecoregions])
        if eol.get(species.id):
            update_species_data(species, eol[species.id])
        else:
            print('--> missing eol id:', species.name)

    eol = jsonload(data_file('external', 'eol.json'))
    for model, kw in [
        (models.Lineage, {}),
        (models.Use, {}),
        (models.TsammalexContributor, {}),
        (models.Languoid, dict(visitor=languoid_visitor)),
        (models.Category, dict(name='categories')),
        (models.Category, dict(name='habitats', visitor=habitat_visitor)),
        (models.Species, dict(visitor=partial(species_visitor, eol))),
        (models.Name, {}),
    ]:
        from_csv(data_file, model, data, **kw)

    def image_url(source_url, type_):
        return re.sub('\.[a-zA-Z]+$', '.jpg', source_url).replace(
            '/original/', '/%s/' % type_)

    for fname in data_files(data_file, 'images.csv'):
        for image in reader(fname, namedtuples=True, delimiter=","):
            if image.species__id not in data['Species']:
                continue

            url = URL(image.source_url)
            if url.host() != 'edmond.mpdl.mpg.de':
                continue

            jsondata = dict(
                url=image.source_url,
                thumbnail=image_url(image.source_url, 'thumbnail'),
                web=image_url(image.source_url, 'web'))

            for k in 'src creator date place comments permission'.split():
                v = getattr(image, k)
                if v:
                    if k == 'permission':
                        jsondata[k] = json.loads(v)
                    elif k == 'src':
                        pref = 'https://lingweb.eva.mpg.de'
                        if v.startswith(pref):
                            v = v[len(pref):]
                        jsondata[k] = v
                    else:
                        jsondata[k] = v
            f = common.Parameter_files(
                object=data['Species'][image.species__id],
                id=image.id,
                name=image.tags,
                jsondata=jsondata,
                mime_type=image.mime_type)
            assert f


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodically whenever data has been updated.
    """
    for vs in DBSession.query(common.ValueSet).options(
            joinedload(common.ValueSet.values)):
        d = []
        for generic_term, words in groupby(
            sorted(vs.values, key=lambda v: v.description), key=lambda v: v.description
        ):
            if generic_term:
                generic_term += ': '
            else:
                generic_term = ''
            d.append(generic_term + ', '.join(nfilter([w.name for w in words])))

        vs.description = '; '.join(d)

    for model in [models.Country, models.Ecoregion]:
        for instance in DBSession.query(model).options(
                joinedload(getattr(model, 'species'))
        ):
            if not instance.species:
                instance.active = False

    # TODO: assign ThePlantList ids!


if __name__ == '__main__':
    initializedb(
        (('data_repos',), dict(action=ExistingDir)), create=main, prime_cache=prime_cache)
    sys.exit(0)
