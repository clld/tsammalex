from clld.web.app import get_configurator

# we must make sure custom models are known at database initialization!
from tsammalex import models


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = get_configurator('tsammalex', settings=settings)
    config.include('clldmpg')
    config.include('tsammalex.datatables')
    config.include('tsammalex.adapters')
    return config.make_wsgi_app()
