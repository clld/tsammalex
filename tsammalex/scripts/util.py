from __future__ import print_function, unicode_literals

from clld.util import slug


def update_species_data(species, d):
    for vn in d.get('eol', {}).get('vernacularNames', []):
        if vn['language'] == 'en' and vn['eol_preferred']:
            if slug(vn['vernacularName']) != slug(species.description):
                #print(species.description, '-->', vn['vernacularName'])
                species.description = vn['vernacularName']
            break

    for an in d.get('eol', {}).get('ancestors', []):
        if not an.get('taxonRank'):
            continue
        for tr in ['family', 'order', 'genus']:
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

    if species.eol_id and not d.get('eol'):
        print('eol_id:', species.eol_id, '-->', None)
        species.eol_id = None
