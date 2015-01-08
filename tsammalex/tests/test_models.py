from clld.scripts.util import Data
from clld.tests.util import TestWithEnv
from clld.db.models import common
from clld.db.meta import DBSession


DATA = {
    'species': [
        'acaciaataxacantha,Acacia ataxacantha,,Flamethorn,Plantae,Fabales,'
        'Fabaceae,Acacia,,,AT1309,BW;ZA,,,,'
        'http://en.wikipedia.org/wiki/Senegalia_ataxacantha,648867,',
    ],
    'lineages': [
        'germanic,Germanic,,germ1287,,,dd0000',
    ],
    'languages': [
        'afr,Afrikaans,germanic,,-33.6,19.4,',
    ],
    'categories': [
        'afr-bome,bome,trees,afr,',
        'afr-plante,plante,plants,afr,',
    ],
    'names': [
        'acaciaataxacantha-afr-0,vlamdoring,afr,acaciaataxacantha,,,,,,,doring,,,,,,,,'
        'afr-bome;afr-plante,,,,,,,,http://www.plantzafrica.com/,,',
    ],
}


class Tests(TestWithEnv):
    __with_custom_language__ = False

    def test_from_csv(self):
        from tsammalex import models as m

        data = Data()
        data.add(common.Contribution, 'tsammalex', id='tsammalex')
        data.add(m.Ecoregion, 'AT1309', id='AT1309')

        for name, cls in [
            ('species', m.Species),
            ('lineages', m.Lineage),
            ('languages', m.Languoid),
            ('categories', m.Category),
            ('names', m.Name)
        ]:
            for row in DATA[name]:
                obj = cls.from_csv(row.split(','), data=data)
                data.add(cls, obj.id, _obj=obj)
