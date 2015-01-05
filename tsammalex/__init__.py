from functools import partial

from six import string_types

from clld.interfaces import ILanguage, IMapMarker
from clld.web.app import get_configurator, menu_item, MapMarker
from clld.web.adapters.base import adapter_factory, Index

# we must make sure custom models are known at database initialization!
from tsammalex import models
from tsammalex.interfaces import IEcoregion

_ = lambda s: s
_('Parameter')
_('Parameters')
_('Source')
_('Sources')
_('Value')
_('Values')


class TsammalexMapMarker(MapMarker):
    def get_icon(self, ctx, req):
        lineage = None
        if ctx and isinstance(ctx, (tuple, list)):
            ctx = ctx[0]

        if ILanguage.providedBy(ctx):
            lineage = ctx.lineage

        if isinstance(ctx, string_types):
            lineage = req.db.query(models.Lineage)\
                .filter(models.Lineage.name == ctx).one()

        if lineage:
            return 'c' + lineage.color


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = get_configurator(
        'tsammalex', (TsammalexMapMarker(), IMapMarker), settings=settings)
    config.include('clldmpg')
    config.include('tsammalex.datatables')
    config.include('tsammalex.maps')
    config.include('tsammalex.adapters')
    config.register_menu(
        ('dataset', partial(menu_item, 'dataset', label='Home')),
        ('values', partial(menu_item, 'values')),
        ('languages', partial(menu_item, 'languages')),
        ('parameters', partial(menu_item, 'parameters')),
        ('ecoregions', lambda ctx, req: (req.route_url('ecoregions'), 'Ecoregions')),
        ('sources', partial(menu_item, 'sources')),
        ('contributors', partial(menu_item, 'contributors', label='Contribute')),
    )
    config.register_resource('ecoregion', models.Ecoregion, IEcoregion, with_index=True)
    config.register_adapter(
        adapter_factory(
            'ecoregion/snippet_html.mako',
            mimetype='application/vnd.clld.snippet+xml',
            send_mimetype='text/html',
            extension='snippet.html'),
        IEcoregion)
    config.register_adapter(
        adapter_factory('ecoregion/detail_html.mako'), IEcoregion)
    config.register_adapter(
        adapter_factory('ecoregion/index_html.mako', base=Index), IEcoregion)

    return config.make_wsgi_app()
