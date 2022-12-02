# pragma: no cover
from itertools import groupby
from functools import partial
import re

from purl import URL
from sqlalchemy.orm import joinedload
from clld.cliutil import Data, bibtex2source, add_language_codes
from clld.db.meta import DBSession
from clld.db.models import common
from clld.lib.bibtex import Database
from csvw.dsv import reader
from clldutils.misc import nfilter
from clldutils.jsonlib import load as jsonload
from clldutils.path import Path

from tsammalex import models
from tsammalex.scripts.util import (
    update_taxon_data, load_ecoregions, from_csv, load_countries, data_files,
)


def main(args):
    def data_file(*comps):
        return Path(args.data_repos).joinpath('tsammalexdata', 'data', *comps)

    data = Data()
    data.add(
        common.Dataset,
        'tsammalex',
        id="tsammalex",
        name="Tsammalex",
        description="Tsammalex: A lexical database on plants and animals",
        publisher_name="Max Planck Institute for Evolutionary Anthropology",
        publisher_place="Leipzig",
        publisher_url="http://www.eva.mpg.de",
        domain='tsammalex.clld.org',
        license='http://creativecommons.org/licenses/by/4.0/',
        contact='dlce.rdm@eva.mpg.de',
        jsondata={
            'license_icon': 'cc-by.png',
            'license_name': 'Creative Commons Attribution 4.0 International License'})
    data.add(common.Contribution, 'tsammalex', name="Tsammalex", id="tsammalex")

    for rec in Database.from_file(data_file('sources.bib'), lowercase=True):
        data.add(models.Bibrec, rec.id, _obj=bibtex2source(rec, cls=models.Bibrec))

    load_ecoregions(data_file, data)
    load_countries(data)
    second_languages = {}

    def languoid_visitor(lang, row, _):
        add_language_codes(
            data, lang, lang.id.split('-')[0], None, glottocode=row[2] or None)
        second_languages[row[0]] = row[8]

    def habitat_visitor(cat, *_):
        cat.is_habitat = True

    def taxon_visitor(auto, taxon, *_):
        if auto.get(taxon.id):
            update_taxon_data(taxon, auto[taxon.id], data)
        else:
            print('--> missing in taxa.json:', taxon.id, taxon.name)
        taxon.countries_str = ' '.join([e.id for e in taxon.countries])
        taxon.ecoregions_str = ' '.join([e.id for e in taxon.ecoregions])

    auto = {s['id']: s for s in jsonload(data_file('taxa.json'))}
    for model, kw in [
        (models.Lineage, {}),
        (models.Use, {}),
        (models.TsammalexContributor, {}),
        (models.Languoid, dict(visitor=languoid_visitor)),
        (models.Category, dict(name='categories')),
        (models.Category, dict(name='habitats', visitor=habitat_visitor)),
        (models.Taxon, dict(visitor=partial(taxon_visitor, auto))),
        (models.Name, dict(filter_=lambda r: 'xxx' not in r[1])),
    ]:
        from_csv(data_file, model, data, **kw)

    for key, ids in second_languages.items():
        target = data['Languoid'][key]
        for lid in models.split_ids(ids):
            if lid in data['Languoid']:
                # we ignore 2nd languages which are not yet in Tsammalex.
                target.second_languages.append(data['Languoid'][lid])

    def image_url(source_url, type_):
        return re.sub('\.[a-zA-Z]+$', '.jpg', source_url).replace(
            '/original/', '/%s/' % type_)

    for fname in data_files(data_file, 'images.csv'):

        for image in reader(fname, namedtuples=True, delimiter=","):
            if image.taxa__id not in data['Taxon']:
                continue

            url = URL(image.source_url)
            if url.host() != 'edmond.mpdl.mpg.de':
                continue

            jsondata = dict(
                url=image.source_url,
                thumbnail=image_url(image.source_url, 'thumbnail'),
                web=image_url(image.source_url, 'web'))

            f = common.Parameter_files(
                object=data['Taxon'][image.taxa__id],
                id=image.id,
                name=image.tags,
                jsondata=jsondata,
                mime_type=image.mime_type)
            for k in 'source creator date place comments permission'.split():
                v = getattr(image, k)
                if v:
                    models.ImageData(key=k, value=v, image=f)


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
                joinedload(getattr(model, 'taxa'))
        ):
            if not instance.taxa:
                instance.active = False

    # TODO: assign ThePlantList ids!
