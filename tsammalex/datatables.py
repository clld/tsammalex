from clld.web.datatables.base import Col
from clld.web.datatables.parameter import Parameters
from clld.web.datatables.value import Values
from clld.web.util.helpers import HTML
from clld.db.util import get_distinct_values
from clld.db.models.common import Parameter

from tsammalex.models import (
    Ecoregion, SpeciesEcoregion,
    Country, SpeciesCountry,
    Category, SpeciesCategory
)


class ThumbnailCol(Col):
    def format(self, item):
        if item.thumbnail:
            return HTML.img(src=self.dt.req.file_url(item.thumbnail))
        return ''


class CatCol(Col):
    __spec__ = (None, None)

    def __init__(self, *args, **kw):
        kw['choices'] = get_distinct_values(self.__spec__[1].name)
        Col.__init__(self, *args, **kw)

    def format(self, item):
        return ', '.join(o.name for o in getattr(item, self.__spec__[0]))

    def search(self, qs):
        return self.__spec__[1].name == qs


class CountryCol(CatCol):
    __spec__ = ('countries', Country)


class CategoryCol(CatCol):
    __spec__ = ('categories', Category)


class EcoregionCol(CatCol):
    __spec__ = ('ecoregions', Ecoregion)


class Species(Parameters):
    def base_query(self, query):
        query = query \
            .outerjoin(SpeciesCategory, SpeciesCategory.species_pk == Parameter.pk) \
            .outerjoin(Category, SpeciesCategory.category_pk == Category.pk)\
            .outerjoin(SpeciesCountry, SpeciesCountry.species_pk == Parameter.pk) \
            .outerjoin(Country, SpeciesCountry.country_pk == Country.pk)\
            .outerjoin(SpeciesEcoregion, SpeciesEcoregion.species_pk == Parameter.pk)\
            .outerjoin(Ecoregion, SpeciesEcoregion.ecoregion_pk == Ecoregion.pk)
        return query.distinct()

    def col_defs(self):
        res = Parameters.col_defs(self)
        res.append(ThumbnailCol(self, 'thumbnail'))
        res.append(CategoryCol(self, 'categories'))
        res.append(EcoregionCol(self, 'ecoregions'))
        res.append(CountryCol(self, 'countries'))
        return res


class Words(Values):
    def col_defs(self):
        res = Values.col_defs(self)
        return res[1:-1]

    def get_options(self):
        if self.parameter:
            return {'bPaginate': False}


def includeme(config):
    config.register_datatable('parameters', Species)
    config.register_datatable('values', Words)
