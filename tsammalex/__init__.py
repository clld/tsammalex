from zope.interface import classImplements
from pyramid.config import Configurator

from clld.interfaces import ILanguage, IMapMarker, IValueSet, IValue
from clld.web.app import MapMarker
from clld.db.models.common import Parameter_files

# we must make sure custom models are known at database initialization!
from tsammalex import models
from tsammalex.interfaces import IEcoregion, IImage


# associate Parameter_files with the IImage interface to make the model work as resource.
classImplements(Parameter_files, IImage)

_ = lambda s: s
_('Parameter')
_('Parameters')
_('Source')
_('Sources')
_('Value')
_('Values')


class TsammalexMapMarker(MapMarker):
    def get_color(self, ctx, req):
        lineage = None
        if ctx and isinstance(ctx, (tuple, list)):
            ctx = ctx[0]

        if ILanguage.providedBy(ctx):
            lineage = ctx.lineage
        elif IValueSet.providedBy(ctx):
            lineage = ctx.language.lineage
        elif IValue.providedBy(ctx):
            lineage = ctx.valueset.language.lineage

        if isinstance(ctx, str):
            lineage = req.db.query(models.Lineage)\
                .filter(models.Lineage.name == ctx).one()

        return lineage.color if lineage else 'ff6600'

    def __call__(self, ctx, req):
        return req.static_url('tsammalex:static/icons/%s.png' % self.get_color(ctx, req))


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('clldmpg')
    config.registry.registerUtility(TsammalexMapMarker(), IMapMarker)
    config.registry.settings['home_comp'].append('contributors')
    config.register_menu(
        ('dataset', dict(label='Home')),
        'values',
        'languages',
        'parameters',
        'ecoregions',
        'sources',
        'images',
        #('contributors', dict(label='Contribute'))
        #('contribute', lambda ctx, req: (req.route_url('help'), 'Contribute!'))
    )
    config.register_resource('ecoregion', models.Ecoregion, IEcoregion, with_index=True)
    config.register_resource('image', Parameter_files, IImage, with_index=True)
    return config.make_wsgi_app()
