from __future__ import print_function, unicode_literals
import json
from itertools import groupby

from clld.util import nfilter
from clld.lib.dsv import reader

from tsammalex.models import Biome, Ecoregion


SOURCE_MAP = {
    'carruthers2000': 'carruthers_wildlife_2000',
    'vanderwalt1999': 'van_der_walt_kalahari_1999',
    'duplessis2005': 'plessis_afrikaans-engels_2005',
    'traillstory1999': 'story_kuha:si_1999',
    'bennetttsoeu2006': 'bennett_multilingual_2006',
    'haackeeiseb2002': 'haacke_khoekhoegowab_2002',
    'picker2002': 'picker_field_2002',
    'snymaned1990': 'snyman_setswana_1990',
    'kilianhatz2003': 'kilian-hatz_khwe_2003',
    'fehnnotes': 'fehn_fieldnotes_',
    'stuartstuart2007': 'stuart_field_2007',
    'dickens1994': 'dickens_english_1994',
    'cillie1997': 'cillie_mammal_1997',
    'guldemannnaumann2011': 'guldemann_inheritance_2011',
    'vanrooyen2001': 'van_rooyen_flowering_2001',
    'dokeetal2008': 'doke_english_2008',
    'burke2007': 'burke_wild_2007',
    'branch1998': 'branch_field_1998',
    'sinclair1994': 'sinclair_field_1994',
    'westphalnotes': 'westphal_fieldnotes_',
    'hannan1987': 'hannan_standard_1987',
    'tanakasugawara2010': 'tanaka_encyclopedia_2010',
    'dickens1986': 'dickens_qhalaxarzi_1986',
    'eksteen1997': 'eksteen_major_1997',
    'kriel1991': 'kriel_new_1991',
    'sinclair2003': 'sinclair_comprehensive_2003',
    'konigheine2008': 'konig_concise_2008',
    'bleek1929': 'bleek_comparative_1929',
    'cunningham': 'cunningham_guide_2009',
    'kgalagaditransfrontierpark2003': '_kgalagadi_2003',
    'bertholdgerlach2011': 'berthold_documentation_2011',
    'leffers2003': 'leffers_gemsbok_2003',
    'leeming2003': 'leeming_scorpions_2003',
    'traillnotes': 'traill_fieldnotes_',
    'traill1994': 'traill_xoo_1994',
    'heine1999': 'heine_ani:_1999',
    'elcin1996': 'elcin_church_council_special_committees_english_1996',
    'viljoenkamupingene1983': 'viljoen_otjiherero:_1983',
    'sandsetal2006': 'sands_1400_2006',
    'visser2001': 'visser_naro_2001',
}


def from_csv(args, model, data, name=None, visitor=None, condition=None, **kw):
    ids = {}
    kw.setdefault('delimiter', ',')
    kw.setdefault('lineterminator', str('\r\n'))
    kw.setdefault('quotechar', '"')
    for row in list(reader(
            args.data_file('dump', (name or model.__csv_name__) + '.csv'), **kw))[1:]:
        if condition and not condition(row):
            continue
        obj = model.from_csv(row, data)
        if obj:
            if hasattr(obj, 'id'):
                if obj.id in ids:
                    print('duplicate id in %s' % (name or model.__csv_name__,))
                    print(row)
                    raise ValueError
                ids[obj.id] = 1
            obj = data.add(model, row[0], _obj=obj)
            if visitor:
                visitor(obj, data)


def update_species_data(species, d):
    if not species.english_name:
        for vn in d.get('eol', {}).get('vernacularNames', []):
            if vn['language'] == 'en' and vn['eol_preferred']:
                species.english_name = vn['vernacularName']
                break

    for an in d.get('eol', {}).get('ancestors', []):
        if not an.get('taxonRank'):
            continue
        for tr in ['kingdom', 'family', 'order', 'genus']:
            if tr == an['taxonRank']:
                curr = getattr(species, tr)
                if curr != an['scientificName']:
                    #print(tr, ':', curr, '-->', an['scientificName'])
                    setattr(species, tr, an['scientificName'])

    for k, v in d.get('wikipedia', {}).items():
        for tr in ['family', 'order', 'genus']:
            if tr == k:
                curr = getattr(species, tr)
                if curr != v:
                    #print(tr, ':', curr, '-->', v)
                    setattr(species, tr, v)

    #if species.eol_id and not d.get('eol'):
    #    print('eol_id:', species.eol_id, '-->', None)
    #    species.eol_id = None


def get_center(arr):
    return reduce(
        lambda x, y: [x[0] + y[0] / len(arr), x[1] + y[1] / len(arr)], arr, [0.0, 0.0])


def load_ecoregions(args, data):
    with open(args.data_file('wwf', 'simplified.json')) as fp:
        ecoregions = json.load(fp)['features']

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
