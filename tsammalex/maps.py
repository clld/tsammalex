from clld.web.maps import ParameterMap, Map, Legend
from clld.web.util.htmllib import HTML, literal
from clld.web.util.helpers import map_marker_img

from tsammalex import ICON_MAP


class SpeciesMap(ParameterMap):
    def get_options(self):
        return {'sidebar': True, 'show_labels': True}


class LanguoidMap(Map):
    def get_options(self):
        return {'show_labels': True, 'icon_size': 20}

    def get_legends(self):
        def value_li(lineage):
            return HTML.label(
                map_marker_img(self.req, lineage),
                literal(lineage),
                style='margin-left: 1em; margin-right: 1em;')

        yield Legend(self, 'lineages', map(value_li, ICON_MAP.keys()), label='Legend')

        for legend in Map.get_legends(self):
            yield legend


def includeme(config):
    config.register_map('parameter', SpeciesMap)
    config.register_map('languages', LanguoidMap)
