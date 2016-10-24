from __future__ import print_function, unicode_literals
from itertools import groupby

from six.moves import reduce
from pycountry import countries
from clldutils.dsv import reader
from clldutils.misc import nfilter
from clldutils.jsonlib import load as jsonload

from tsammalex.models import Biome, Ecoregion, Country


def data_files(data_file, name):
    files = [data_file(name)]
    heath = files[0].parent.joinpath('heath', files[0].name)
    if heath.exists():
        files.append(heath)
    return files


def from_csv(data_file, model, data, name=None, visitor=None, filter_=None):
    if filter_ is None:
        filter_ = lambda r: True
    kw = {'delimiter': ',', 'lineterminator': str('\r\n'), 'quotechar': '"'}
    for fname in data_files(data_file, (name or model.__csv_name__) + '.csv'):
        for row in list(reader(fname, **kw))[1:]:
            if row and filter_(row):
                try:
                    obj = model.from_csv(row, data)
                except (KeyError, IndexError):
                    obj = None
                    print(fname)
                    print(row)
                    raise
                if obj:
                    obj = data.add(model, row[0], _obj=obj)
                    if visitor:
                        visitor(obj, row, data)


def update_taxon_data(taxon, d, data):
    for attr in [
        'eol_id', 'gbif_id', 'catalogueoflife_url', 'wikipedia_url', 'description'
    ]:
        setattr(taxon, attr, d.get(attr))

    if d.get('english_name'):
        taxon.english_name = d['english_name']

    if d.get('taxonRank'):
        taxon.rank = d['taxonRank'].lower()

    too_low = False
    for rank in 'kingdom phylum class order family genus'.split():
        too_low = too_low or rank == taxon.rank
        setattr(taxon, rank, None if too_low else d.get(rank))

    for attr, model in dict(ecoregions='Ecoregion', countries='Country').items():
        collection = getattr(taxon, attr)
        for id_ in d[attr]:
            collection.append(data[model][id_])


def get_center(arr):
    return reduce(
        lambda x, y: [x[0] + y[0] / len(arr), x[1] + y[1] / len(arr)], arr, [0.0, 0.0])


def load_countries(data):
    for country in countries:
        data.add(Country, country.alpha2, id=country.alpha2, name=country.name)


def load_ecoregions(data_file, data):
    ecoregions = jsonload(data_file('ecoregions.json'))['features']

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
                Biome, props['BIOME'],
                id=str(int(props['BIOME'])),
                name=name,
                description=color or 'ffffff')
        centroid = (None, None)
        f = sorted(features, key=lambda _f: _f['properties']['AREA'])[-1]
        if f['geometry']:
            coords = f['geometry']['coordinates'][0]
            if f['geometry']['type'] == 'MultiPolygon':
                coords = coords[0]
            centroid = get_center(coords)

        polygons = nfilter([_f['geometry'] for _f in features])
        data.add(
            Ecoregion, eco_code,
            id=eco_code,
            name=props['ECO_NAME'],
            description=props['G200_REGIO'],
            latitude=centroid[1],
            longitude=centroid[0],
            biome=biome,
            area=props['area_km2'],
            gbl_stat=Ecoregion.gbl_stat_map[int(props['GBL_STAT'])],
            realm=Ecoregion.realm_map[props['REALM']],
            jsondata=dict(polygons=polygons))
