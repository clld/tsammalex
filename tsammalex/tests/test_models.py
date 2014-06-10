from clld.tests.util import TestWithEnv
from clld.db.models import common


class Tests(TestWithEnv):
    def test_Word(self):
        from tsammalex.models import Word

        class Data(dict):
            def add(self, *args, **kw):
                return

        vs = common.ValueSet(id='vs')
        vs.parameter = common.Parameter(id='p')
        vs.language = common.Language(id='l')
        data = Data(
            ValueSet=dict(vs=vs),
            Languoid=dict(l=vs.language),
            Species=dict(p=vs.parameter),
            Contribution=dict(tsammalex=common.Contribution(id='c')))
        l = Word(id='w', valueset=vs)
        row = l.to_csv()
        l2 = Word.from_csv(row, data=data)
        self.assertEquals(l2.id, l.id)

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
        from tsammalex.models import Species

        l = Species(id='l')
        row = l.to_csv()
        l2 = Species.from_csv(row)
        self.assertEquals(l2.id, l.id)

    def test_Languoid(self):
        from tsammalex.models import Languoid

        l = Languoid(id='l', latitude=23.3)
        row = l.to_csv()
        l2 = Languoid.from_csv(row)
        self.assertEquals(l2.id, l.id)
        self.assertAlmostEqual(l.latitude, l2.latitude)
