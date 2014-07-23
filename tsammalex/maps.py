from clld.web.maps import ParameterMap, Map, Legend, Layer
from clld.web.util.htmllib import HTML, literal
from clld.web.util.helpers import map_marker_img
from clld.db.meta import DBSession
from clld.db.util import as_int

from tsammalex.models import ICON_MAP, Biome


class SpeciesMap(ParameterMap):
    def get_options(self):
        return {
            'sidebar': True, 'show_labels': True,
            #'on_init': JS('TSAMMALEX.ecoregions')
        }


class LanguoidMap(Map):
    def get_options(self):
        return {'show_labels': True, 'icon_size': 20, 'max_zoom': 8}

    def get_legends(self):
        def value_li(lineage):
            return HTML.label(
                map_marker_img(self.req, lineage),
                literal(lineage),
                style='margin-left: 1em; margin-right: 1em;')

        yield Legend(self, 'lineages', map(value_li, ICON_MAP.keys()), label='Legend')

        for legend in Map.get_legends(self):
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
                        style='background-color: #%s; border: 1px solid black; margin-right: 1em; opacity: 0.5;'
                              % biome.description),
                    literal(biome.name),
                    style='margin-left: 1em; margin-right: 1em;'))
        yield Legend(self, 'categories', items)


def includeme(config):
    config.register_map('parameter', SpeciesMap)
    config.register_map('languages', LanguoidMap)
    config.register_map('ecoregions', EcoregionsMap)
