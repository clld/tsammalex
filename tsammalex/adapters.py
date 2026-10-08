from itertools import chain

from clld.web.adapters.geojson import (
    GeoJsonParameterMultipleValueSets, GeoJson, GeoJsonLanguages,
)
from clld.web.adapters.base import Representation
from clld.interfaces import ILanguage, IIndex, IParameter

from tsammalex.interfaces import IEcoregion
from tsammalex.cdstar2s3 import s3url

from pyramid import httpexceptions


class GeoJsonEcoregions(GeoJson):
    def featurecollection_properties(self, ctx, req):
        return {'name': "WWF's Terrestrial Ecoregions of the Afrotropics"}

    def get_features(self, ctx, req):
        for ecoregion in ctx.get_query():
            for polygon in ecoregion.jsondata['polygons']:
                yield {
                    'type': 'Feature',
                    'properties': {
                        'id': ecoregion.id,
                        'label': '%s %s' % (ecoregion.id, ecoregion.name),
                        'color': ecoregion.biome.description,
                        'language': {'id': ecoregion.id},
                        'latlng': [ecoregion.latitude, ecoregion.longitude],
                    },
                    'geometry': polygon,
                }


class GeoJsonTaxa(GeoJsonParameterMultipleValueSets):
    def feature_properties(self, ctx, req, p):
        return {
            'lineage': p[0].lineage,
            'label': ', '.join(v.name for v in chain(*[vs.values for vs in p[1]]))}


class GeoJsonLanguoids(GeoJsonLanguages):
    def feature_properties(self, ctx, req, feature):
        return {'lineage': feature.lineage}


class LanguagePdf(Representation):
    mimetype = 'application/pdf'
    extension = 'pdf'

    def render(self, ctx, req):
        url = s3url(ctx.jsondata.get('pdf_url'))
        if url:
            raise httpexceptions.HTTPFound(url)
        raise httpexceptions.HTTPNotFound(url)


def includeme(config):
    config.register_adapter(LanguagePdf, ILanguage)
    config.register_adapter(GeoJsonEcoregions, IEcoregion, IIndex)
    config.register_adapter(GeoJsonTaxa, IParameter)
    config.register_adapter(GeoJsonLanguoids, ILanguage, IIndex)
