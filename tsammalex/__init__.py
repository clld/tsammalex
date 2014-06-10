from functools import partial

from clld import interfaces
from clld.web.app import get_configurator, menu_item, MapMarker

# we must make sure custom models are known at database initialization!
from tsammalex import models
assert models
from tsammalex import views

_ = lambda s: s
_('Parameter')
_('Parameters')

ICON_MAP = {
    'Bantu': 'ffff00',
    'Khoe': '00ffff',
    'Tuu': '66ff33',
    "Kx'a": '990099',
    'Germanic': 'dd0000',
}


class TsammalexMapMarker(MapMarker):
    def __call__(self, ctx, req):
        lineage = None
        if ctx and isinstance(ctx, (tuple, list)):
            ctx = ctx[0]

        if interfaces.ILanguage.providedBy(ctx):
            lineage = ctx.lineage

        if ctx in ICON_MAP:
            lineage = ctx

        if lineage:
            icon = ICON_MAP.get(lineage, 'ffff00')
            return req.static_url('clld:web/static/icons/c%s.png' % icon)

        return super(TsammalexMapMarker, self).__call__(ctx, req)  # pragma: no cover


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = get_configurator(
        'tsammalex', (TsammalexMapMarker(), interfaces.IMapMarker), settings=settings)
    config.include('clldmpg')
    config.include('tsammalex.datatables')
    config.include('tsammalex.maps')
    config.include('tsammalex.adapters')
    config.register_menu(
        ('dataset', partial(menu_item, 'dataset', label='Home')),
        ('languages', partial(menu_item, 'languages')),
        ('parameters', partial(menu_item, 'parameters')),
        ('ecoregions', lambda ctx, req: (req.route_url('ecoregions'), 'Ecoregions')),
    )
    config.add_route_and_view(
        'ecoregions', '/ecoregions', renderer='ecoregions.mako', view=views.ecoregions)
    return config.make_wsgi_app()
