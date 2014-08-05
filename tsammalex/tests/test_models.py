from clld.tests.util import TestWithEnv
from clld.db.models import common
from clld.db.meta import DBSession


class Tests(TestWithEnv):
    __with_custom_language__ = False

    def test_Word(self):
        from tsammalex.models import Word, Bibrec, Species, Category

        #class Data(dict):
        #    def add(self, *args, **kw):
        #        return  # pragma: no cover

        vs = common.ValueSet(id='vs')
        vs.parameter = Species(id='p')
        vs.language = common.Language(id='l')
        cat = Category(id='c')
        vs.parameter.categories.append(cat)
        data = dict(
            ValueSet={'p-l': vs},
            Languoid=dict(l=vs.language),
            Species=dict(p=vs.parameter),
            Category=dict(c=cat),
            Contribution=dict(tsammalex=common.Contribution(id='c')),
            Bibrec={v.id: v for v in DBSession.query(Bibrec)})
        l = Word(id='w', valueset=vs)
        row = l.to_csv()
        l2 = Word.from_csv(row, data=data)
        self.assertEquals(l2.id, l.id)
        row[14] = 'picker2002[12]'
        Word.from_csv(row, data=data)
        row[14] = 'picker2002'
        row[15] = 'c'
        Word.from_csv(row, data=data)
        data['ValueSet'] = {'p-l': vs}
        Word.from_csv(row, data=data)
        self.assert_(list(Word.csv_query(DBSession)))

    def test_TsammalexEditor(self):
        from tsammalex.models import TsammalexEditor

        l = TsammalexEditor(contributor=common.Contributor(name='l'))
        assert l.csv_head()
        row = l.to_csv()
        l2 = TsammalexEditor.from_csv(
            row, data={'TsammalexEditor': dict(l=l.contributor)})
        self.assertEquals(l2.contributor.name, l.contributor.name)

    def test_Species(self):
        from tsammalex.models import Species, Ecoregion, Country

        l = Species(id='l')
        row = l.to_csv()
        l2 = Species.from_csv(row)
        self.assertEquals(l2.id, l.id)

        row = ['id', 'name', 'description', None, None, None, None, None, None, None]
        data = {}
        for cls in [Country, Ecoregion]:
            data[cls.mapper_name()] = {}
            for i, obj in enumerate(DBSession.query(cls)):
                data[cls.mapper_name()][obj.id] = obj
            row.append(','.join(data[cls.mapper_name()].keys()))
        Species.from_csv(row, data=data)

    def test_Languoid(self):
        from tsammalex.models import Languoid

        l = Languoid(id='l', latitude=23.3)
        row = l.to_csv()
        l2 = Languoid.from_csv(row)
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
