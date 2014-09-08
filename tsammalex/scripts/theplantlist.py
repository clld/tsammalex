"""
http://www.theplantlist.org/1.1/browse/-/

<ul id="nametree">


<!--[if lt IE 9]></ul><ul class="nametree"><![endif]-->

<li id="A">
<a href="/1.1/browse/A/Acanthaceae/"><i class="family">Acanthaceae</i></a>
</li>


http://www.theplantlist.org/1.1/browse/B/Conocephalaceae/Conocephalaceae.csv

ID,Major group,Family,Genus hybrid marker,Genus,Species hybrid marker,Species,Infraspecific rank,Infraspecific epithet,Authorship,Taxonomic status in TPL,Nomenclatural status from original data source,Confidence level,Source,Source id,IPNI id,Publication,Collation,Page,Date
tro-35185073,B,Conocephalaceae,,Conocephalum,,"conicum",,"","(L.) Underw.",Accepted,,M,TRO,35185073,,"Bot. Gaz.","20: 67","67","1895"
tro-35200546,B,Conocephalaceae,,Conocephalum,,"japonicum",,"","(Thunb.) Grolle",Accepted,,M,TRO,35200546,,"J. Hattori Bot. Lab.","55: 501","501","1984"
tro-35216419,B,Conocephalaceae,,Conocephalum,,"salebrosum",,"","Szweyk., Buczkowska & Odrzykoski",Accepted,,M,TRO,35216419,,"Pl. Syst. Evol.","253: 146","146","2005"
tro-35188163,B,Conocephalaceae,,Conocephalum,,"supradecompositum",,"","Stephani",Unresolved,,L,TRO,35188163,,"Sp. Hepat.","1: 1412","1412","1899"
tro-35215091,B,Conocephalaceae,,Conocephalum,,"trioicum",,"","F. Weber",Unresolved,,L,TRO,35215091,,"Prim. Fl. Holsat.","82","82","1780"
tro-35208072,B,Conocephalaceae,,Hepatica,,"supradecomposita",,"","Stephani ex C. Massal.",Unresolved,,L,TRO,35208072,,"Mem. Accad. Agric. Verona","72(3): 52","52","1897"
tro-35210298,B,Conocephalaceae,,Nemoursia,,"tuberculata",,"","Mrat",Unresolved,,L,TRO,35210298,,"Ann. Agric. Franc.","2(7): 12","12","1840"

"""
from __future__ import unicode_literals, absolute_import, division, print_function
import json
from io import open as iopen

import requests
from bs4 import BeautifulSoup as bs
import transaction

from clld.scripts.util import parsed_args
from clld.lib.dsv import reader
from clld.db.meta import DBSession
from clld.db.models.common import Parameter
from clld.util import slug


BASE_URL = "http://www.theplantlist.org"


def get(path):
    return requests.get(BASE_URL + path).text


def main(args, reload=False):
    species = {}
    db = args.data_file('theplantlist', 'db.json')
    if reload:
        for a in bs(get('/1.1/browse/-/')).find('ul', id='nametree').find_all('a'):
            with iopen(args.data_file('theplantlist', a.text + '.csv'), 'w', encoding='utf8') as fp:
                fp.write(get(a['href'] + a.text + '.csv'))

    if db.exists():
        with open(db) as fp:
            species = json.load(fp)
    else:
        for p in args.data_file('theplantlist').files('*.csv'):
            for row in reader(p, namedtuples=True, delimiter=','):
                if row.Taxonomic_status_in_TPL == 'Accepted':
                    id_ = slug(row.Genus + row.Species)
                    species[id_] = row.ID
        with open(db, 'w') as fp:
            json.dump(species, fp)

    with transaction.manager:
        found = 0
        for p in DBSession.query(Parameter):
            id_ = slug(p.name)
            if id_ in species:
                found += 1
                p.tpl_id = species[id_]

    print(found)

if __name__ == '__main__':
    main(parsed_args())
