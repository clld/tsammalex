from path import path

from clld.tests.util import TestWithApp

import tsammalex


class Tests(TestWithApp):
    __cfg__ = path(tsammalex.__file__)\
        .dirname().joinpath('..', 'development.ini').abspath()
    __setup_db__ = False

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
        # TODO: docx adapter with images requires internet!
        #self.app.get('/parameters/pantheraleo.docx')

    def test_language(self):
        self.app.get_dt('/languages')
        self.app.get_html('/languages')
        self.app.get_html('/languages/huc')
        self.app.get('/languages/huc.docx')
        self.app.get_json('/languages.geojson')

    def test_name(self):
        self.app.get_dt('/values')
        self.app.get_dt('/values?language=ngh')
        self.app.get_dt('/values?language=ngh&sSearch_7=n')
        self.app.get_dt('/values?paramter=pantheraleo')
