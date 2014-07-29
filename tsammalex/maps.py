from copy import copy

from clld.web.maps import ParameterMap, Map, Legend, Layer
from clld.web.util.htmllib import HTML, literal
from clld.web.util.helpers import JS
from clld.db.meta import DBSession
from clld.db.util import as_int, get_distinct_values

from tsammalex.models import Biome, Languoid


OPTIONS = {'show_labels': True, 'icon_size': 20, 'max_zoom': 8}


def li(eid, label, checked=False):
    input_attrs = dict(
        type='radio',
        class_='stay-open lineage inline',
        name='lineage',
        value=label,
        onclick=JS("TSAMMALEX.toggle_languages")(eid))
    if checked:
        input_attrs['checked'] = 'checked'
    return HTML.label(
        HTML.input(**input_attrs),
        ' ',
        label,
        class_='stay-open',
        style="margin-left:5px; margin-right:5px;",
    )


def lineage_legend(map_):
    items = [li(map_.eid, '--any--', checked=True)]
    for l in get_distinct_values(Languoid.lineage):
        items.append(li(map_.eid, l))

    return Legend(map_, 'lineage', items, stay_open=True)


class SpeciesMap(ParameterMap):
    def get_options(self):
        opts = copy(OPTIONS)
        opts['height'] = 300
        opts['hash'] = False
        return opts

    def get_legends(self):
        yield lineage_legend(self)

        for legend in super(SpeciesMap, self).get_legends():
            yield legend


class LanguoidMap(Map):
    def get_options(self):
        return OPTIONS

    def get_legends(self):
        yield lineage_legend(self)

        for legend in super(LanguoidMap, self).get_legends():
            yield legend


class EcoregionsMap(Map):
    def get_options(self):
        return {
            'info_route': 'ecoregion',
            'no_showlabels': True,
            'max_zoom': 8,
        }

    def get_layers(self):
        yield Layer(
            'ecoregions',
            'WWF Eco Regions',
            self.req.route_url('ecoregions_alt', ext='geojson'))

    def get_legends(self):
        items = []

        for biome in DBSession.query(Biome)\
                .filter(Biome.description != 'ffffff')\
                .order_by(as_int(Biome.id)):
            items.append(
                HTML.label(
                    HTML.span(
                        literal('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'),
                        style='background-color: #%s;' % biome.description,
                        class_='biome-color'),
                    literal(biome.name),
                    style='margin-left: 1em; margin-right: 1em;'))
        yield Legend(self, 'categories', items)


def includeme(config):
    config.register_map('parameter', SpeciesMap)
    config.register_map('languages', LanguoidMap)
    config.register_map('ecoregions', EcoregionsMap)
