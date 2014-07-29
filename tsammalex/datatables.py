# coding: utf8
from sqlalchemy import and_, null
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
    Word, Variety, WordVariety,
    Languoid,
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


class CategoryCol(Col):
    def __init__(self, dt, *args, **kw):
        self.lang_pks = [l.pk for l in dt.languages]
        q = DBSession.query(Category.name).order_by(Category.name)
        if self.lang_pks:
            q = q.filter(Category.language_pk.in_(self.lang_pks))
        else:
            q = q.filter(Category.language_pk == null())
        kw['choices'] = [r[0] for r in q]
        Col.__init__(self, dt, *args, **kw)

    def format(self, item):
        return ', '.join(o.name for o in item.categories if
                         (self.lang_pks and o.language_pk in self.lang_pks) or
                         (not self.lang_pks and not o.language_pk))

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
                query = query.join(
                    self._langs[i],
                    and_(self._langs[i].language_pk == lang.pk,
                         self._langs[i].parameter_pk == Parameter.pk))

            query = query \
                .outerjoin(SpeciesCategory, SpeciesCategory.species_pk == Parameter.pk) \
                .outerjoin(Category,
                           and_(SpeciesCategory.category_pk == Category.pk,
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
        res = Parameters.col_defs(self)[1:]
        res[0].js_args['sTitle'] = 'Species'
        res.append(Col(self, 'description', sTitle='English name')),
        if self.languages:
            for i, lang in enumerate(self.languages):
                res.append(CommonNameCol(self, 'cn%s' % i, lang, self._langs[i]))
        res.append(
            Col(self, 'genus', model_col=Species.genus, sTitle='Basic term (Eng)')),
        # Umbenennung "Family" > "Order, family" (mit Filter für alle Einträge für
        # Ordnungen und Familien, ähnlich bisheriger "Categories")
        res.append(Col(self, 'family', model_col=Species.family, sTitle='Order, family')),
        res.append(ThumbnailCol(self, 'thumbnail'))
        res.append(CategoryCol(self, 'categories', bSortable=False))
        res.append(er_col)
        res.append(CountryCol(self, 'countries', bSortable=False))
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


class VarietiesCol(Col):
    __kw__ = dict(bSortable=False)

    def search(self, qs):
        return Variety.pk == int(qs)

    def format(self, item):
        return ', '.join(v.name for v in item.varieties)


class Words(Values):
    def base_query(self, query):
        query = Values.base_query(self, query)
        if self.language:
            query = query.outerjoin(WordVariety, Variety)
            query = query.options(joinedload_all(Value.valueset, ValueSet.parameter))
        return query

    def col_defs(self):
        res = []
        if self.language:
            res = [
                LinkCol(
                    self, 'species',
                    model_col=Parameter.name,
                    get_object=lambda i: i.valueset.parameter),
                Col(
                    self, 'name',
                    sTitle='English name',
                    model_col=Parameter.description,
                    get_object=lambda i: i.valueset.parameter),
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
        res.append(Col(self, 'word', sTitle='Word form', model_col=Value.name))
        res.append(Col(self, 'phonetic', sTitle='IPA', model_col=Word.phonetic))
        res.append(Col(self, 'grammatical_notes', model_col=Word.grammatical_info))
        res.append(Col(self, 'exact meaning', model_col=Value.description))
        if self.language and self.language.varieties:
            res.append(VarietiesCol(
                self, 'variety',
                choices=[(v.pk, v.name) for v in self.language.varieties]))
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
