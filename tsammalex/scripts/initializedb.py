# coding: utf8
# pragma: no cover
from __future__ import unicode_literals, division, absolute_import, print_function
import sys
import json
from itertools import groupby

from path import path
from clld.scripts.util import (
    initializedb, Data, bibtex2source, glottocodes_by_isocode, add_language_codes,
)
from clld.db.meta import DBSession
from clld.db.models import common
from clld.lib.dsv import reader
from clld.util import nfilter

from tsammalex import models
from tsammalex.scripts import wiki


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

    for i, spec in enumerate([('naumann', "Christfried Naumann")]):
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


biome_map = {
    1: ('Tropical & Subtropical Moist Broadleaf Forests', '008001'),
    2: ('Tropical & Subtropical Dry Broadleaf Forests', '557715'),
    3: ('Tropical & Subtropical Coniferous Forests', ''),
    4: ('Temperate Broadleaf & Mixed Forests', ''),
    5: ('Temperate Conifer Forests', ''),
    6: ('Boreal Forests/Taiga', ''),
    7: ('Tropical & Subtropical Grasslands, Savannas & Shrublands', '98ff66'),
    8: ('Temperate Grasslands, Savannas & Shrublands', ''),
    9: ('Flooded Grasslands & Savannas', '0265fe'),
    10: ('Montane Grasslands & Shrublands', 'cdffcc'),
    11: ('Tundra', ''),
    12: ('Mediterranean Forests, Woodlands & Scrub', 'cc9900'),
    13: ('Deserts & Xeric Shrublands', 'feff99'),
    14: ('Mangroves', '870083'),
}


def get_center(arr):
    return reduce(
        lambda x, y: [x[0] + y[0] / len(arr), x[1] + y[1] / len(arr)], arr, [0.0, 0.0])


def main(args):
    data, contrib, glottolog = get_metadata()

    refs = wiki.get_refs(args)
    for rec in refs.records:
        data.add(models.Bibrec, rec.id, _obj=bibtex2source(rec, cls=models.Bibrec))

    with open(args.data_file('wwf', 'simplified.json')) as fp:
        ecoregions = json.load(fp)['features']

    for eco_code, features in groupby(
            sorted(ecoregions, key=lambda e: e['properties']['eco_code']),
            key=lambda e: e['properties']['eco_code']):
        features = list(features)
        props = features[0]['properties']
        if int(props['BIOME']) not in biome_map:
            continue
        biome = data['Biome'].get(props['BIOME'])
        if not biome:
            name, color = biome_map[int(props['BIOME'])]
            biome = data.add(
                models.Biome, props['BIOME'],
                id=str(int(props['BIOME'])),
                name=name,
                description=color or 'ffffff')
        centroid = (None, None)
        f = sorted(features, key=lambda _f: _f['properties']['AREA'])[-1]
        if f['geometry']:
            try:
                coords = f['geometry']['coordinates'][0]
                if f['geometry']['type'] == 'MultiPolygon':
                    coords = coords[0]
                centroid = get_center(coords)
            except:
                print(f)
                raise

        polygons = nfilter([f['geometry'] for f in features])
        data.add(
            models.Ecoregion, eco_code,
            id=eco_code,
            name=props['ECO_NAME'],
            description=props['G200_REGIO'],
            latitude=centroid[1],
            longitude=centroid[0],
            biome=biome,
            area=props['area_km2'],
            gbl_stat=models.Ecoregion.gbl_stat_map[int(props['GBL_STAT'])],
            realm=models.Ecoregion.realm_map[props['REALM']],
            jsondata=dict(polygons=polygons))

    from_csv(
        args, models.Bibrec, data, condition=lambda row: row[0] not in data['Bibrec'])

    for model in [
        models.Variety,
        models.Country,
        models.Category,
    ]:
        from_csv(args, model, data)

    def visitor(lang, data):
        if lang.id in glottolog:
            add_language_codes(data, lang, lang.id, glottolog)

    from_csv(args, models.Languoid, data, visitor=visitor)
    from_csv(args, models.Species, data)

    for image in reader(
            args.data_file('dump', 'images.csv'),
            namedtuples=True,
            delimiter=",",
            lineterminator='\r\n'
    ):
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


if __name__ == '__main__':
    initializedb(create=main, prime_cache=prime_cache)
    sys.exit(0)
