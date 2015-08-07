from __future__ import unicode_literals
from copy import copy

from clld.web.maps import ParameterMap, Map, Legend, Layer, FilterLegend
from clld.web.util.helpers import map_marker_img
from clld.web.util.htmllib import HTML, literal
from clld.db.meta import DBSession
from clld.db.util import as_int

from tsammalex.models import Biome


OPTIONS = {'show_labels': True, 'icon_size': 20, 'max_zoom': 8}


class LineageFilter(FilterLegend):
    def li_label(self, item):
        if item == '--any--':
            return item
        return HTML.span(map_marker_img(self.map.req, item), item)


class SpeciesMap(ParameterMap):
    def __init__(self, ctx, req, eid='map', col=None, dt=None):
        Map.__init__(self, ctx, req, eid=eid)
        self.col, self.dt = col, dt

    def get_options(self):
        opts = copy(OPTIONS)
        opts['height'] = 300
        opts['hash'] = False
        return opts

    def get_legends(self):
        yield LineageFilter(self, 'TSAMMALEX.getLineage', col=self.col, dt=self.dt)

        for legend in super(SpeciesMap, self).get_legends():
            yield legend


class LanguoidMap(Map):
    def __init__(self, ctx, req, eid='map', col=None, dt=None):
        Map.__init__(self, ctx, req, eid=eid)
        self.col, self.dt = col, dt

    def get_options(self):
        return OPTIONS

    def get_legends(self):
        yield LineageFilter(self, 'TSAMMALEX.getLineage', col=self.col, dt=self.dt)

        for legend in super(LanguoidMap, self).get_legends():
            yield legend

    def get_layers(self):
        #yield Layer(
        #    'ecoregions',
        #    'WWF Eco Regions',
        #    self.req.route_url('ecoregions_alt', ext='geojson'))

        for layer in Map.get_layers(self):
            yield layer


class EcoregionsMap(Map):
    def get_options(self):
        return {
            'info_route': 'ecoregion_alt',
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
    for route_name, cls in dict(
        parameter=SpeciesMap,
        languages=LanguoidMap,
        ecoregions=EcoregionsMap,
    ).items():
        config.register_map(route_name, cls)
