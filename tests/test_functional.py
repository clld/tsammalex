import pytest


@pytest.mark.parametrize(
    "method,path",
    [
        ('get_html', '/'),
        ('get_html', '/ecoregions/AT0101'),
        ('get_html', '/ecoregions'),
        ('get_dt', '/ecoregions'),
        ('get_json', '/ecoregions.geojson'),
        ('get_html', '/parameters'),
        ('get_dt', '/parameters'),
        ('get_dt', '/parameters?languages=afr'),
        ('get_dt', '/parameters?er=a&sSearch_6=a'),
        ('get_html', '/parameters/pantheraleo'),
        ('get_json', '/parameters/pantheraleo.geojson'),
        ('get', '/parameters/pantheraleo.docx?test=1'),
        ('get_dt', '/languages'),
        ('get_html', '/languages'),
        ('get_html', '/languages/huc'),
        ('get_json', '/languages.geojson'),
        ('get_dt', '/values'),
        ('get_dt', '/values?language=ngh'),
        ('get_dt', '/values?language=ngh&sSearch_7=n'),
        ('get_dt', '/values?paramter=pantheraleo'),
        ('get_dt', '/contributors'),
        ('get_html', '/valuesets/abelmoschusesculentus-yornoso'),
        ('get_html', '/valuesets/abelmoschusesculentus-yornoso.snippet.html'),
    ])
def test_pages(app, method, path):
    getattr(app, method)(path)
