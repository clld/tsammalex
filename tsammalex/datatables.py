from sqlalchemy.orm import aliased, joinedload, joinedload_all

from clld.web.datatables.base import Col, LinkCol
from clld.web.datatables.parameter import Parameters
from clld.web.datatables.value import Values
from clld.web.util.helpers import HTML, external_link, linked_references
from clld.db.util import get_distinct_values
from clld.db.models.common import Parameter, Value, Language, ValueSet

from tsammalex.models import (
    Ecoregion, SpeciesEcoregion,
    Country, SpeciesCountry,
    Category, SpeciesCategory, Species
)


class ThumbnailCol(Col):
    __kw__ = dict(bSearchable=False, bSortable=False)

    def format(self, item):
        item = self.get_obj(item)
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


class SpeciesTable(Parameters):
    def __init__(self, *args, **kw):
        self.genus = aliased(Species)
        Parameters.__init__(self, *args, **kw)

    def base_query(self, query):
        query = query.filter(Species.is_genus == False) \
            .outerjoin(SpeciesCategory, SpeciesCategory.species_pk == Parameter.pk) \
            .outerjoin(Category, SpeciesCategory.category_pk == Category.pk)\
            .outerjoin(SpeciesCountry, SpeciesCountry.species_pk == Parameter.pk) \
            .outerjoin(Country, SpeciesCountry.country_pk == Country.pk)\
            .outerjoin(SpeciesEcoregion, SpeciesEcoregion.species_pk == Parameter.pk)\
            .outerjoin(Ecoregion, SpeciesEcoregion.ecoregion_pk == Ecoregion.pk)\
            .outerjoin(self.genus, self.genus.pk == Species.genus_pk)\
            .options(
                joinedload(Species.genus),
                joinedload(Species.categories),
                joinedload(Species.ecoregions),
                joinedload(Species.countries))
        return query.distinct()

    def col_defs(self):
        res = Parameters.col_defs(self)[1:]
        res[0].js_args['sTitle'] = 'Species'
        res.append(Col(self, 'description', sTitle='Name')),
        res.append(LinkCol(self, 'genus', model_col=self.genus.name, get_object=lambda i: i.genus)),
        res.append(Col(self, 'family', model_col=Species.family)),
        res.append(ThumbnailCol(self, 'thumbnail'))
        res.append(CategoryCol(self, 'categories', bSortable=False))
        res.append(EcoregionCol(self, 'ecoregions', bSortable=False))
        res.append(CountryCol(self, 'countries', bSortable=False))
        return res


class RefsCol(Col):
    __kw__ = dict(bSearchable=False, bSortable=False)

    def format(self, item):
        lis = []
        if item.valueset.source:
            s = item.valueset.source
            if s.startswith('http://'):
                label = s
                for t in 'wikimedia wikipedia plantzafrica'.split():
                    if t in s:
                        label = t
                        break
                lis.append(external_link(s, label))
            else:
                lis.append(s)
        lis.append(linked_references(self.dt.req, item.valueset))
        return HTML.ul(*lis, class_='unstyled')


class MdCol(Col):
    __kw__ = dict(bSearchable=False, bSortable=False)

    def format(self, item):
        return HTML.ul(*[HTML.li(HTML.i(v)) for v in item.jsondatadict.values()], class_='unstyled')


class Words(Values):
    def base_query(self, query):
        query = Values.base_query(self, query)
        if self.language:
            query = query.options(joinedload_all(Value.valueset, ValueSet.parameter))
        return query

    def col_defs(self):
        res = []
        if self.language:
            res = [
                ThumbnailCol(self, '_', get_object=lambda i: i.valueset.parameter),
                LinkCol(
                    self, 'species',
                    model_col=Parameter.name,
                    get_object=lambda i: i.valueset.parameter),
                Col(
                    self, 'name',
                    model_col=Parameter.description,
                    get_object=lambda i: i.valueset.parameter),
            ]
        elif self.parameter:
            res = [
                LinkCol(
                    self, 'language',
                    model_col=Language.name,
                    get_object=lambda i: i.valueset.language)
            ]
        res.append(Col(self, 'word', model_col=Value.name))
        if self.language:
            res.append(Col(self, 'exact meaning', model_col=Value.description))
            res.append(MdCol(self, 'md'))
        res.append(RefsCol(self, 'references'))
        return res

    def get_options(self):
        if self.parameter:
            return {'bPaginate': False}


def includeme(config):
    config.register_datatable('parameters', SpeciesTable)
    config.register_datatable('values', Words)
