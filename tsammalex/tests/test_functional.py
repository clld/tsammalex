from clldutils.path import Path

from clld.tests.util import TestWithApp

import tsammalex


class Tests(TestWithApp):
    __cfg__ = Path(tsammalex.__file__)\
        .parent.joinpath('..', 'development.ini').resolve()

    def test_home(self):
        self.app.get('/', status=200)

    def test_ecoregion(self):
        self.app.get_html('/ecoregions/AT0101')
        self.app.get_html('/ecoregions')
        self.app.get_dt('/ecoregions')
        self.app.get_json('/ecoregions.geojson')

    def test_parameter(self):
        self.app.get_html('/parameters')
        self.app.get_dt('/parameters')
        self.app.get_dt('/parameters?languages=afr')
        self.app.get_dt('/parameters?er=a&sSearch_6=a')
        self.app.get_html('/parameters/pantheraleo')
        self.app.get_json('/parameters/pantheraleo.geojson')
        self.app.get('/parameters/pantheraleo.docx?test=1')

    def test_language(self):
        self.app.get_dt('/languages')
        self.app.get_html('/languages')
        self.app.get_html('/languages/huc')
        self.app.get_json('/languages.geojson')

    def test_name(self):
        self.app.get_dt('/values')
        self.app.get_dt('/values?language=ngh')
        self.app.get_dt('/values?language=ngh&sSearch_7=n')
        self.app.get_dt('/values?paramter=pantheraleo')

    def test_contributors(self):
        self.app.get_dt('/contributors')

    def test_valueset(self):
        self.app.get_html('/valuesets/abelmoschusesculentus-yornoso')
        self.app.get_html('/valuesets/abelmoschusesculentus-yornoso.snippet.html')
