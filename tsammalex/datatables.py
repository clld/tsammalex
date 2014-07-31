# coding: utf8
from sqlalchemy import and_, null, or_
from sqlalchemy.orm import joinedload, joinedload_all, aliased

from clld.web.datatables.base import DataTable, Col, LinkCol, IdCol
from clld.web.datatables.parameter import Parameters
from clld.web.datatables.value import Values
from clld.web.datatables.language import Languages
from clld.web.util.helpers import HTML, external_link, linked_references, button, icon
from clld.db.util import get_distinct_values, as_int, icontains
from clld.db.meta import DBSession
from clld.db.models.common import Parameter, Value, Language, ValueSet
from clld.util import nfilter

from tsammalex.models import (
    Ecoregion, SpeciesEcoregion, Biome,
    Country, SpeciesCountry,
    Category, SpeciesCategory, Species,
    Word,
    Languoid,
)
from tsammalex.util import format_classification


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


class CategoryCol(Col):
    def __init__(self, dt, name, languages, **kw):
        assert languages
        self.lang_dict = {l.pk: l for l in languages}
        q = DBSession.query(Category.name).order_by(Category.name)\
            .filter(Category.language_pk.in_(list(self.lang_dict.keys())))
        kw['choices'] = [r[0] for r in q]
        Col.__init__(self, dt, name, **kw)

    def _cat(self, cat):
        if len(self.lang_dict) > 1:
            return '%s (%s)' % (cat.name, self.lang_dict[cat.language_pk].id)
        return cat.name

    def format(self, item):
        obj = self.get_obj(item)
        names = [
            self._cat(o) for o in obj.categories if o.language_pk in self.lang_dict]
        return HTML.ul(*[HTML.li(name) for name in names], class_="unstyled")

    def search(self, qs):
        return Category.name == qs


class EcoregionCol(CatCol):
    __spec__ = ('ecoregions', Ecoregion)

    def __init__(self, *args, **kw):
        kw['choices'] = [
            er.name for er in
            DBSession.query(Ecoregion).join(SpeciesEcoregion).order_by(Ecoregion.id)]
        Col.__init__(self, *args, **kw)


class CommonNameCol(Col):
    def __init__(self, dt, name, lang, alias, **kw):
        self.lang = lang
        self.alias = alias
        kw['sTitle'] = 'Name in %s' % lang.name
        Col.__init__(self, dt, name, **kw)

    def format(self, item):
        for vs in item.valuesets:
            if vs.language_pk == self.lang.pk:
                return vs.description
        return ''

    def order(self):
        return self.alias.description

    def search(self, qs):
        return icontains(self.alias.description, qs)


class ClassificationCol(Col):
    def __init__(self, *args, **kw):
        choices = set()
        for row in DBSession.query(Species.order, Species.family, Species.genus):
            for name in row:
                if name:
                    choices.add(name)
        kw['choices'] = sorted(choices)
        Col.__init__(self, *args, **kw)

    def format(self, item):
        return format_classification(item)

    def search(self, qs):
        return or_(Species.order == qs, Species.family == qs, Species.genus == qs)

    def order(self):
        return [Species.order, Species.family, Species.genus]


class SpeciesTable(Parameters):
    def __init__(self, req, *args, **kw):
        Parameters.__init__(self, req, *args, **kw)
        if kw.get('languages'):
            self.languages = kw['languages']
        elif 'languages' in req.params:
            self.languages = nfilter([
                Language.get(id_, default=None)
                for id_ in req.params['languages'].split(',')])
        else:
            self.languages = []
        self._langs = [
            aliased(ValueSet, name='l%s' % i) for i in range(len(self.languages))]

    def base_query(self, query):
        query = query \
            .outerjoin(SpeciesCountry, SpeciesCountry.species_pk == Parameter.pk) \
            .outerjoin(Country, SpeciesCountry.country_pk == Country.pk)\
            .outerjoin(SpeciesEcoregion, SpeciesEcoregion.species_pk == Parameter.pk)\
            .outerjoin(Ecoregion, SpeciesEcoregion.ecoregion_pk == Ecoregion.pk)\
            .options(
                joinedload(Species.categories),
                joinedload(Species.ecoregions),
                joinedload(Species.countries),
                #joinedload(Parameter._files)
                )
        if self.languages:
            for i, lang in enumerate(self.languages):
                query = query.outerjoin(
                    self._langs[i],
                    and_(self._langs[i].language_pk == lang.pk,
                         self._langs[i].parameter_pk == Parameter.pk))

            query = query \
                .filter(or_(*[
                    self._langs[i].pk != null() for i in range(len(self._langs))]))\
                .outerjoin(SpeciesCategory, SpeciesCategory.species_pk == Parameter.pk) \
                .outerjoin(
                    Category,
                    and_(
                        SpeciesCategory.category_pk == Category.pk,
                        Category.language_pk.in_([l.pk for l in self.languages])))\
                .options(joinedload_all(Parameter.valuesets, ValueSet.values))
        else:
            query = query\
                .outerjoin(SpeciesCategory, SpeciesCategory.species_pk == Parameter.pk) \
                .outerjoin(Category,
                           and_(SpeciesCategory.category_pk == Category.pk,
                                Category.language_pk == null()))
        return query.distinct()

    def col_defs(self):
        er_col = EcoregionCol(self, 'ecoregions', bSortable=False)
        if 'er' in self.req.params:
            er_col.js_args['sFilter'] = self.req.params['er']

        res = [
            LinkCol(self, 'name', sTitle='Species'),
            Col(self, 'description', sTitle='English name'),
            ClassificationCol(self, 'order', sTitle='Biological classification'),
            ThumbnailCol(self, 'thumbnail'),
            # TODO: second thumbnail?
        ]
        if self.languages:
            for i, lang in enumerate(self.languages):
                res.append(CommonNameCol(self, 'cn%s' % i, lang, self._langs[i]))
            res.append(CategoryCol(self, 'categories', self.languages, bSortable=False))

        res.extend([
            er_col,
            CountryCol(self, 'countries', bSortable=False)])
        # TODO: characteristics col?
        return res

    def xhr_query(self):
        res = Parameters.xhr_query(self)
        if self.languages:
            res['languages'] = ','.join(l.id for l in self.languages)
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
        lis.append(linked_references(self.dt.req, item.valueset))
        return HTML.ul(*lis, class_='unstyled')


class MultiCategoriesCol(Col):
    __kw__ = dict(bSortable=False, bSearchable=False)

    def format(self, item):
        names = [
            o.name for o in item.valueset.parameter.categories
            if o.language_pk == item.valueset.language_pk]
        return HTML.ul(*[HTML.li(name) for name in names], class_="unstyled")


class Words(Values):
    def base_query(self, query):
        query = Values.base_query(self, query)
        if self.language:
            query = query\
                .outerjoin(SpeciesCategory, SpeciesCategory.species_pk == Parameter.pk)\
                .outerjoin(
                    Category,
                    and_(
                        SpeciesCategory.category_pk == Category.pk,
                        Category.language_pk == self.language.pk))
        return query.options(joinedload_all(
            Value.valueset, ValueSet.parameter, Species.categories))

    def col_defs(self):
        res = []
        if self.language:
            res = [
                LinkCol(
                    self, 'species',
                    model_col=Parameter.name,
                    get_object=lambda i: i.valueset.parameter),
                #Col(
                #    self, 'name',
                #    sTitle='English name',
                #    model_col=Parameter.description,
                #    get_object=lambda i: i.valueset.parameter),
                ThumbnailCol(self, '_', get_object=lambda i: i.valueset.parameter),
            ]
        elif self.parameter:
            res = [
                LinkCol(
                    self, 'language',
                    model_col=Language.name,
                    get_object=lambda i: i.valueset.language),
                Col(self, 'lineage',
                    model_col=Languoid.lineage,
                    format=lambda i: i.valueset.language.lineage)
            ]
        res.append(LinkCol(self, 'name', sTitle='Word form'))
        res.append(Col(self, 'blt', sTitle='Generic term', model_col=Value.description))
        res.append(Col(self, 'phonetic', sTitle='IPA', model_col=Word.phonetic))
        res.append(Col(self, 'grammatical_notes', model_col=Word.grammatical_info))
        res.append(Col(self, 'exact meaning', model_col=Word.meaning))
        if self.language:
            res.append(CategoryCol(
                self, 'categories',
                [self.language],
                get_object=lambda i: i.valueset.parameter))
        if self.parameter:
            res.append(MultiCategoriesCol(self, 'categories'))
        res.append(Col(self, 'general_notes', model_col=Word.notes))
        res.append(RefsCol(self, 'references'))
        return res

    def get_options(self):
        if self.parameter:
            return {'bPaginate': False}


class Languoids(Languages):
    def col_defs(self):
        res = Languages.col_defs(self)
        return res[:2] + [
            Col(self, 'lineage',
                model_col=Languoid.lineage,
                choices=get_distinct_values(Languoid.lineage))
        ] + res[2:]


class BiomeCol(Col):
    def __init__(self, dt, name, **kw):
        kw['choices'] = DBSession.query(Biome.id, Biome.name)\
            .order_by(as_int(Biome.id))
        Col.__init__(self, dt, name, **kw)

    def search(self, qs):
        return Biome.id == qs

    def order(self):
        return as_int(Biome.id)

    def format(self, item):
        return item.biome.name


class LinkToMapCol(Col):
    __kw__ = dict(bSearchable=False, bSortable=False)

    def format(self, item):
        return button(
            icon('globe'),
            href="#map",
            onclick='TSAMMALEX.highlightEcoregion(CLLD.Maps.map.marker_map.'
                    + item.id + ')')


class Ecoregions(DataTable):
    def base_query(self, query):
        return query\
            .join(Ecoregion.biome)\
            .filter(Ecoregion.realm == 'Afrotropics')\
            .options(joinedload(Ecoregion.biome), joinedload(Ecoregion.species))

    def col_defs(self):
        return [
            IdCol(self, 'id', sTitle='Code'),
            LinkCol(self, 'name'),
            BiomeCol(self, 'category'),
            Col(self, 'status',
                sDescription=Ecoregion.gbl_stat.doc,
                model_col=Ecoregion.gbl_stat,
                choices=get_distinct_values(Ecoregion.gbl_stat)),
            LinkToMapCol(self, 'm', sTitle=''),
            Col(self, 'w', sTitle='', format=lambda i: external_link(i.wwf_url(), 'WWF'))
        ]

    def get_options(self):
        return {'iDisplayLength': 200, 'bPaginate': False}


def includeme(config):
    config.register_datatable('parameters', SpeciesTable)
    config.register_datatable('values', Words)
    config.register_datatable('languages', Languoids)
    config.register_datatable('ecoregions', Ecoregions)
