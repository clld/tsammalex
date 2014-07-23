from clld.tests.util import TestWithEnv
from clld.db.models import common
from clld.db.meta import DBSession


class Tests(TestWithEnv):
    __with_custom_language__ = False

    def test_Word(self):
        from tsammalex.models import Word, Variety, Bibrec

        class Data(dict):
            def add(self, *args, **kw):
                return

        vs = common.ValueSet(id='vs')
        vs.parameter = common.Parameter(id='p')
        vs.language = common.Language(id='l')
        data = Data(
            ValueSet={},
            Languoid=dict(l=vs.language),
            Species=dict(p=vs.parameter),
            Contribution=dict(tsammalex=common.Contribution(id='c')),
            Variety={v.id: v for v in DBSession.query(Variety)},
            Bibrec={v.id: v for v in DBSession.query(Bibrec)})
        l = Word(id='w', valueset=vs)
        row = l.to_csv()
        l2 = Word.from_csv(row, data=data)
        self.assertEquals(l2.id, l.id)
        row[8] = 'ngh-e'
        row[10] = 'picker2002[12]'
        Word.from_csv(row, data=data)
        row[10] = 'picker2002'
        Word.from_csv(row, data=data)
        data['ValueSet'] = {'p-l': vs}
        Word.from_csv(row, data=data)
        self.assert_(list(Word.csv_query(DBSession)))

    def test_Variety(self):
        from tsammalex.models import Variety

        l = Variety(id='l')
        row = l.to_csv()
        l2 = Variety.from_csv(row)
        self.assertEquals(l2.id, l.id)

    def test_TsammalexEditor(self):
        from tsammalex.models import TsammalexEditor

        l = TsammalexEditor(contributor=common.Contributor(name='l'))
        assert l.csv_head()
        row = l.to_csv()
        l2 = TsammalexEditor.from_csv(
            row, data={'TsammalexEditor': dict(l=l.contributor)})
        self.assertEquals(l2.contributor.name, l.contributor.name)

    def test_Species(self):
        from tsammalex.models import Species, Category, Ecoregion, Country

        l = Species(id='l')
        row = l.to_csv()
        l2 = Species.from_csv(row)
        self.assertEquals(l2.id, l.id)

        row = ['id', 'name', 'description', None, None, None, None]
        data = {}
        for cls in [Country, Category, Ecoregion]:
            data[cls.mapper_name()] = {}
            for i, obj in enumerate(DBSession.query(cls)):
                data[cls.mapper_name()][obj.id] = obj
            row.append(','.join(data[cls.mapper_name()].keys()))
        Species.from_csv(row, data=data)

    def test_Languoid(self):
        from tsammalex.models import Languoid, Variety

        l = Languoid(id='l', latitude=23.3)
        v = Variety(id='v')
        l.varieties.append(v)
        row = l.to_csv()
        l2 = Languoid.from_csv(row, data=dict(Variety=dict(v=v)))
        self.assertEquals(l2.id, l.id)
        self.assertAlmostEqual(l.latitude, l2.latitude)

    def test_Bibrec(self):
        from tsammalex.models import Bibrec

        rec = Bibrec(id='b')
        Bibrec.from_csv(rec.to_csv())

    def test_misc(self):
        from tsammalex.models import Category, Ecoregion, Country

        for cls in [Category, Ecoregion, Country]:
            obj = cls.first()
            assert obj.csv_head()
