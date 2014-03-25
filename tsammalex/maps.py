from clld.web.maps import ParameterMap


class SpeciesMap(ParameterMap):
    def get_options(self):
        return {'sidebar': True, 'show_labels': True}


def includeme(config):
    config.register_map('parameter', SpeciesMap)