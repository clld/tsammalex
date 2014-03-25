from functools import partial

from clld.web.app import get_configurator, menu_item

# we must make sure custom models are known at database initialization!
from tsammalex import models

_ = lambda s: s
_('Parameter')
_('Parameters')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = get_configurator('tsammalex', settings=settings)
    config.include('clldmpg')
    config.include('tsammalex.datatables')
    config.include('tsammalex.maps')
    config.include('tsammalex.adapters')
    config.register_menu(
        ('dataset', partial(menu_item, 'dataset', label='Home')),
        ('languages', partial(menu_item, 'languages')),
        ('parameters', partial(menu_item, 'parameters')),
    )
    return config.make_wsgi_app()
