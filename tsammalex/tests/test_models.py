from __future__ import unicode_literals

from clld.scripts.util import Data
from clld.tests.util import TestWithEnv
from clld.db.models import common


DATA = {
    'contributors': [
        'nc,"Naumann, Christfried",,1,,"M P I",Tsammalex,http://example.org,',
    ],
    'taxa': [
        'acaciaataxacantha,Acacia ataxacantha,,,Flamethorn,Plantae,,,Fabales,'
        'Fabaceae,Acacia,,,BW;ZA,,,ref1;ref2[20],',
    ],
    'lineages': [
        'germanic,Germanic,,germ1287,,,dd0000',
    ],
    'languages': [
        'afr,English,stan1293,,"English is a ...",germanic,,,Northern Europe,'
    ],
    'categories': [
        'afr-bome,bome,trees,afr,',
        'afr-plante,plante,plants,afr,',
    ],
    'names': [
        'acaciaataxacantha-afr-0,vlamdoring,afr,acaciaataxacantha,,,,,,,doring,,,,,,,,'
        'afr-bome;afr-plante,,,,,,,,http://www.plantzafrica.com/,ref1;ref2[20],',
    ],
}


class Tests(TestWithEnv):
    __with_custom_language__ = False

    def test_from_csv(self):
        from tsammalex import models as m

        data = Data()
        data.add(common.Dataset, 'tsammalex', id='tsammalex')
        data.add(common.Contribution, 'tsammalex', id='tsammalex')
        data.add(m.Ecoregion, 'AT1309', id='AT1309')
        data.add(m.Bibrec, 'ref1', id='ref1')
        data.add(m.Bibrec, 'ref2', id='ref2')

        for name, cls in [
            ('contributors', m.TsammalexContributor),
            ('taxa', m.Taxon),
            ('lineages', m.Lineage),
            ('languages', m.Languoid),
            ('categories', m.Category),
            ('names', m.Name)
        ]:
            for row in DATA[name]:
                obj = cls.from_csv(row.split(','), data=data)
                data.add(cls, obj.id, _obj=obj)
