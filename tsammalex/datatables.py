# coding: utf8
from sqlalchemy import and_, null, or_, false
from sqlalchemy.orm import joinedload, joinedload_all, aliased

from clld.web.datatables.base import DataTable, Col, LinkCol, IdCol
from clld.web.datatables.parameter import Parameters
from clld.web.datatables.value import Values
from clld.web.datatables.language import Languages
from clld.web.datatables.contributor import Contributors, AddressCol, NameCol, UrlCol
from clld.web.util.helpers import (
    HTML, external_link, linked_references, button, icon, map_marker_img,
)
from clld.db.util import get_distinct_values, as_int, icontains
from clld.db.meta import DBSession
from clld.db.models.common import Parameter, Value, Language, ValueSet, Contributor
from clld.util import nfilter

from tsammalex.models import (
    Ecoregion, SpeciesEcoregion, Biome,
    Country, Lineage,
    Category, Species,
    Name, TsammalexContributor, TsammalexEditor,
    Languoid, NameReference, NameCategory,
)
from tsammalex.util import format_classification


class ContribNameCol(NameCol):
    def format(self, item):
        res = NameCol.format(self, item)
        if item.editor:
            return HTML.span(res, HTML.span(' [ed.]'))
        return res


class TsammalexContributors(Contributors):
    def base_query(self, query):
        return query.outerjoin(TsammalexEditor)

    def col_defs(self):
        return [
            ContribNameCol(self, 'name'),
            Col(self, 'section', model_col=TsammalexContributor.sections),
            AddressCol(self, 'affiliation', model_col=TsammalexContributor.address),
            Col(self, 'project', model_col=TsammalexContributor.research_project),
            UrlCol(self, 'homepage'),
        ]


class ThumbnailCol(Col):
    __kw__ = dict(bSearchable=False, bSortable=False)

    def format(self, item):
        item = self.get_obj(item)
        if item.thumbnail:
            return HTML.img(src=item.thumbnail)
        return ''


class _CategoryCol(Col):
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


class EcoregionCol(Col):
    def __init__(self, *args, **kw):
        kw['choices'] = [
            er.name for er in
            DBSession.query(Ecoregion).join(SpeciesEcoregion).order_by(Ecoregion.id)]
        kw['model_col'] = Species.ecoregions_str
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
        query = query.options(joinedload(Parameter._files))
        if self.languages:
            for i, lang in enumerate(self.languages):
                query = query.outerjoin(
                    self._langs[i],
                    and_(self._langs[i].language_pk == lang.pk,
                         self._langs[i].parameter_pk == Parameter.pk))

            query = query \
                .filter(or_(*[
                    self._langs[i].pk != null() for i in range(len(self._langs))]))\
                .options(joinedload_all(Parameter.valuesets, ValueSet.values))
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
            res.append(_CategoryCol(self, 'categories', self.languages, bSortable=False))

        res.extend([
            er_col,
            Col(self, 'countries',
                model_col=Species.countries_str,
                choices=get_distinct_values(Country.name),
                bSortable=False)])
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
        if item.source:
            s = item.source
            if s.startswith('http://'):
                label = s
                for t in 'wikimedia wikipedia plantzafrica'.split():
                    if t in s:
                        label = t
                        break
                lis.append(external_link(s, label))
        lis.append(linked_references(self.dt.req, item))
        return HTML.ul(*lis, class_='unstyled')


class CategoriesCol(Col):
    __kw__ = dict(bSortable=False)

    def __init__(self, dt, *args, **kw):
        kw['choices'] = [(c.pk, c.name) for c in DBSession.query(Category)\
            .filter(Category.is_habitat == false())\
            .filter(Category.language == dt.language)]
        Col.__init__(self, dt, *args, **kw)

    def format(self, item):
        return HTML.ul(*[HTML.li(o.name) for o in item.categories], class_="unstyled")

    def search(self, qs):
        return NameCategory.category_pk == int(qs)


class LineageCol(Col):
    def __init__(self, dt, name, **kw):
        kw['choices'] = [
            r[0] for r in DBSession.query(Lineage.name).order_by(Lineage.name)]
        kw['model_col'] = Lineage.name
        Col.__init__(self, dt, name, **kw)

    def format(self, item):
        if hasattr(item, 'valueset'):
            item = item.valueset.language
        return HTML.span(map_marker_img(self.dt.req, item), item.lineage.id)


class EnglishNameCol(LinkCol):
    def get_attrs(self, item):
        return {'label': self.get_obj(item).english_name}


class Names(Values):
    def base_query(self, query):
        query = Values.base_query(self, query)
        if self.language:
            query = query\
                .outerjoin(NameCategory)\
                .outerjoin(Name.habitats)
        if not self.language and not self.parameter:
            query = query.join(ValueSet.language).join(ValueSet.parameter)
        return query.options(
            joinedload_all(Value.valueset, ValueSet.parameter),
            joinedload_all(Name.references, NameReference.source))

    def col_defs(self):
        get_param = lambda i: i.valueset.parameter
        shared = {col.name: col for col in [
            LinkCol(self, 'name'),
            Col(self, 'ipa', sTitle='IPA', model_col=Name.ipa),
            Col(self, 'grammatical_info', model_col=Name.grammatical_info),
            LinkCol(
                self, 'language',
                model_col=Language.name,
                get_object=lambda i: i.valueset.language),
            LinkCol(self, 'species', model_col=Parameter.name, get_object=get_param),
            ThumbnailCol(self, 'thumbnail', sTitle='', get_object=get_param),
            RefsCol(self, 'references'),
            Col(self, 'meaning', model_col=Value.description),
        ]}
        if self.language:
            return [
                shared['name'],
                Col(self, 'blt', sTitle='Basic term', model_col=Name.basic_term),
                CategoriesCol(self, 'categories'),
                shared['species'],
                shared['thumbnail'],
                shared['ipa'],
                shared['grammatical_info'],
                shared['meaning'],
                shared['references'],
            ]
        if self.parameter:
            return [
                shared['language'],
                LineageCol(self, 'lineage'),
                shared['name'],
                shared['ipa'],
                shared['grammatical_info'],
                shared['meaning'],
                shared['references'],
            ]
            res.append(LinkCol(self, 'name'))
            res.append(Col(self, 'blt', sTitle='Generic term', model_col=Value.description))
            res.append(Col(self, 'ipa', sTitle='IPA', model_col=Name.ipa))
            res.append(Col(self, 'grammatical_notes', model_col=Name.grammatical_info))
        return [
            shared['name'],
            shared['language'],
            shared['ipa'],
            shared['grammatical_info'],
            shared['species'],
            EnglishNameCol(
                self, 'english name',
                model_col=Species.english_name,
                get_object=get_param),
            shared['thumbnail'],
            shared['references'],
        ]

    def get_options(self):
        if self.parameter:
            return {'bPaginate': False}


class Languoids(Languages):
    def base_query(self, query):
        return query.join(Languoid.lineage)

    def col_defs(self):
        res = Languages.col_defs(self)
        return res[:2] + [LineageCol(self, 'lineage')] + res[2:]


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
    config.register_datatable('values', Names)
    config.register_datatable('languages', Languoids)
    config.register_datatable('languages', Languoids)
    config.register_datatable('contributors', TsammalexContributors)
