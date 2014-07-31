# coding: utf8
# pragma: no cover
from __future__ import unicode_literals, division, absolute_import, print_function
import sys
import json
from itertools import groupby

from sqlalchemy.orm import joinedload
from path import path
from clld.scripts.util import (
    initializedb, Data, bibtex2source, glottocodes_by_isocode, add_language_codes,
)
from clld.db.meta import DBSession
from clld.db.models import common
from clld.lib.dsv import reader
from clld.util import nfilter, slug

from tsammalex import models
from tsammalex.scripts import wiki
from tsammalex.scripts.util import update_species_data, load_ecoregions


files_dir = path('/home/robert/venvs/clld/tsammalex/data/files')


def get_metadata():
    data = Data()
    dataset = common.Dataset(
        id="tsammalex",
        name="Tsammalex",
        description="A lexical database on plants and animals (preliminary version)",
        publisher_name="Max Planck Institute for Evolutionary Anthropology",
        publisher_place="Leipzig",
        publisher_url="http://www.eva.mpg.de",
        domain='tsammalex.clld.org',
        license='http://creativecommons.org/licenses/by/3.0/',
        contact='naumann@eva.mpg.de',
        jsondata={
            'license_icon': 'cc-by.png',
            'license_name': 'Creative Commons Attribution 3.0 Unported License'})
    DBSession.add(dataset)

    for i, spec in enumerate([
            ('naumann', "Christfried Naumann"),
            ('forkel', 'Robert Forkel')]):
        DBSession.add(common.Editor(
            dataset=dataset,
            ord=i + 1,
            contributor=common.Contributor(id=spec[0], name=spec[1])))

    contrib = data.add(common.Contribution, 'tsammalex', name="Tsammalex", id="tsammalex")
    return data, contrib, glottocodes_by_isocode('postgresql://robert@/glottolog3')


def from_csv(args, model, data, visitor=None, condition=None, **kw):
    kw.setdefault('delimiter', ',')
    kw.setdefault('lineterminator', str('\r\n'))
    kw.setdefault('quotechar', '"')
    for row in list(
            reader(args.data_file('dump', model.__csv_name__ + '.csv'), **kw))[1:]:
        if condition and not condition(row):
            continue
        obj = data.add(model, row[0], _obj=model.from_csv(row, data))
        if visitor:
            visitor(obj, data)


def main(args):
    data, contrib, glottolog = get_metadata()

    refs = wiki.get_refs(args)
    for rec in refs.records:
        data.add(models.Bibrec, rec.id, _obj=bibtex2source(rec, cls=models.Bibrec))

    from_csv(
        args, models.Bibrec, data, condition=lambda row: row[0] not in data['Bibrec'])

    load_ecoregions(args, data)

    def visitor(lang, data):
        if lang.id in glottolog:
            add_language_codes(data, lang, lang.id.split('-')[0], glottolog)
        if lang.id == 'eng':
            lang.is_english = True

    from_csv(args, models.Languoid, data, visitor=visitor)
    for model in [
        models.Country,
        models.Category,
    ]:
        from_csv(args, model, data)

    from_csv(args, models.Species, data)

    for image in reader(
            args.data_file('dump', 'images.csv'),
            namedtuples=True,
            delimiter=",",
            lineterminator='\r\n'
    ):
        #
        # TODO: respect flags thumbnail1 and thumbnail2!
        #
        # id,species_id,name,mime_type,src,width,height,author,date,place,comments,
        # keywords,permission
        jsondata = dict(width=int(image.width), height=int(image.height))
        for k in 'src author date place comments keywords permission'.split():
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
            object=data['Species'][image.species_id],
            id=image.id,
            name=image.name,
            jsondata=jsondata,
            mime_type=image.mime_type)
        assert f
        #
        # TODO: handle new images!?
        #
        # f.create(files_dir, wiki.get(args, img[n]['src'], html=False))

    from_csv(args, models.Word, data)


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

    with open(args.data_file('classification.json')) as fp:
        sdata = json.load(fp)

    for species in DBSession.query(models.Species):
        update_species_data(species, sdata[species.id])


if __name__ == '__main__':
    initializedb(create=main, prime_cache=prime_cache)
    sys.exit(0)
