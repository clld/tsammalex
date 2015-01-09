# coding: utf8
from sqlalchemy import and_, null, or_, false, true
from sqlalchemy.orm import joinedload, joinedload_all, aliased, contains_eager

from clld.web.datatables.base import DataTable, Col, LinkCol, IdCol
from clld.web.datatables.parameter import Parameters
from clld.web.datatables.value import Values
from clld.web.datatables.language import Languages
from clld.web.datatables.contributor import Contributors, AddressCol, NameCol, UrlCol
from clld.web.util.helpers import (
    HTML, external_link, linked_references, button, icon, map_marker_img, maybe_license_link,
)
from clld.db.util import get_distinct_values, as_int, icontains
from clld.db.meta import DBSession
from clld.db.models.common import Parameter, Value, Language, ValueSet, Parameter_files
from clld.util import nfilter

from tsammalex.models import (
    Ecoregion, SpeciesEcoregion, Biome, ImageData,
    Country, Lineage,
    Category, Species,
    Name, TsammalexContributor, TsammalexEditor,
    Languoid, NameReference, NameCategory, Use, NameUse, NameHabitat,
)
from tsammalex.util import format_classification, collapsed


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
        thumbnail = self.get_obj(item).image_url('thumbnail')
        if thumbnail:
            return HTML.img(src=thumbnail)
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


class EcoregionCountryColBase(Col):
    __kw__ = {'sortable': False}

    def __init__(self, model, species_col, *args, **kw):
        self.species_col = species_col
        kw['choices'] = [
            (o.id, '%s %s' % (o.id, o.name)) for o in
            DBSession.query(model).filter(model.active == true()).order_by(model.id)]
        kw['model_col'] = getattr(Species, self.species_col)
        Col.__init__(self, *args, **kw)

    def search(self, qs):
        return icontains(self.model_col, qs)

    def content(self, items):
        return ' '.join(items)

    def format(self, item):
        items = (getattr(item, self.species_col) or '').split()
        content = self.content(items)
        if len(items) < 4:
            return content
        return collapsed('%s-%s' % (self.species_col, item.id), content)


class EcoregionCol(EcoregionCountryColBase):
    def __init__(self, *args, **kw):
        EcoregionCountryColBase.__init__(self, Ecoregion, 'ecoregions_str', *args, **kw)

    def content(self, items):
        return HTML.ul(*[
            HTML.li(HTML.a(eid, href=self.dt.req.route_url('ecoregion', id=eid)))
            for eid in items],
            class_='unstyled')


class CountriesCol(EcoregionCountryColBase):
    def __init__(self, *args, **kw):
        EcoregionCountryColBase.__init__(self, Country, 'countries_str', *args, **kw)


class CommonNameCol(Col):
    def __init__(self, dt, name, lang, alias, **kw):
        self.lang = lang
        self.alias = alias
        kw['sTitle'] = 'Colloquial names in %s' % lang.name
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
        query = query\
            .outerjoin(SpeciesEcoregion, Ecoregion)\
            .options(joinedload(Parameter._files))
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
        er_col = EcoregionCol(self, 'ecoregions')
        if 'er' in self.req.params:
            er_col.js_args['sFilter'] = self.req.params['er']

        res = [
            LinkCol(self, 'name', sTitle='Species'),
            Col(self, 'english_name', model_col=Species.english_name),
            ClassificationCol(self, 'order', sTitle='Biological classification'),
            ThumbnailCol(self, 'thumbnail'),
            # TODO: second thumbnail?
            Col(self, 'characteristics', model_col=Species.characteristics)
        ]
        if self.languages:
            for i, lang in enumerate(self.languages):
                res.append(CommonNameCol(self, 'cn%s' % i, lang, self._langs[i]))
            #res.append(_CategoryCol(self, 'categories', self.languages, bSortable=False))

        res.extend([er_col, CountriesCol(self, 'countries')])
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


class RelationsCol(Col):
    __kw__ = dict(bSortable=False)
    __rel_name__ = None

    def __init__(self, dt, *args, **kw):
        kw['choices'] = [(c.pk, c.name) for c in self._choices(dt)]
        Col.__init__(self, dt, *args, **kw)

    def _choices(self, dt):
        raise NotImplemented()

    def format(self, item):
        return HTML.ul(
            *[HTML.li(o.name) for o in getattr(item, self.__rel_name__)],
            class_="unstyled")

    def search(self, qs):
        raise NotImplemented()


class CategoriesCol(RelationsCol):
    __rel_name__ = 'categories'

    def _choices(self, dt):
        return DBSession.query(Category) \
            .filter(Category.is_habitat == false()) \
            .filter(Category.language == dt.language)

    def search(self, qs):
        return NameCategory.category_pk == int(qs)


class HabitatsCol(RelationsCol):
    __rel_name__ = 'habitats'

    def _choices(self, dt):
        return DBSession.query(Category)\
            .filter(Category.is_habitat == true())\
            .filter(Category.language == dt.language)

    def search(self, qs):
        return NameHabitat.category_pk == int(qs)


class UsesCol(RelationsCol):
    __rel_name__ = 'uses'

    def _choices(self, dt):
        return DBSession.query(Use)

    def search(self, qs):
        return NameUse.use_pk == int(qs)


class LineageCol(Col):
    def __init__(self, dt, name, **kw):
        kw['choices'] = [
            r[0] for r in DBSession.query(Lineage.name).order_by(Lineage.name)]
        kw['model_col'] = Lineage.name
        Col.__init__(self, dt, name, **kw)

    def format(self, item):
        if hasattr(item, 'valueset'):
            item = item.valueset.language
        return HTML.span(map_marker_img(self.dt.req, item), item.lineage.name)


class EnglishNameCol(LinkCol):
    def get_attrs(self, item):
        return {'label': self.get_obj(item).english_name}


class Names(Values):
    def __init__(self, req, model, eid=None, **kw):
        self._type = req.params.get('type', kw.pop('type', ''))
        Values.__init__(self, req, model, eid=eid, **kw)
        self.eid = self.eid + self._type

    def xhr_query(self):
        res = Values.xhr_query(self)
        if self._type:
            res['type'] = self._type
        return res

    def base_query(self, query):
        query = Values.base_query(self, query)
        if self.language:
            query = query\
                .outerjoin(NameCategory)\
                .outerjoin(NameHabitat)\
                .outerjoin(Name.uses)\
                .options(
                    contains_eager(Name.uses),
                    joinedload(Name.habitats),
                    joinedload(Name.categories))
        if not self.language and not self.parameter:
            query = query.join(ValueSet.language).join(ValueSet.parameter)
        if not self.parameter:
            query = query.options(joinedload(
                Value.valueset, ValueSet.parameter, Parameter._files))
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
            cols = [
                shared['name'],
                Col(self, 'blt', sTitle='Basic term', model_col=Name.basic_term),
                CategoriesCol(self, 'categories'),
                shared['species'],
                shared['thumbnail'],
            ]
            if self._type == 'cultural':
                cols.extend([
                    HabitatsCol(self, 'habitats'),
                    Col(self, 'introduced', model_col=Name.introduced),
                    UsesCol(self, 'uses', sTitle='Usage'),
                    Col(self, 'importance', model_col=Name.importance),
                    Col(self, 'associations', model_col=Name.associations),
                ])
            else:
                cols.extend([
                    shared['ipa'],
                    shared['grammatical_info'],
                    shared['meaning'],
                    #shared['references'],
                    UsesCol(self, 'uses', sTitle='Usage'),
                ])
            return cols
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
        return res[:2] + [
            Col(self, 'glottocode', model_col=Languoid.glottocode),
            LineageCol(self, 'lineage'),
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
            .options(contains_eager(Ecoregion.biome), joinedload(Ecoregion.species))

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


class MD5Col(LinkCol):
    def format(self, item):
        return HTML.span(LinkCol.format(self, item), style="font-family: monospace;")


class _ThumbnailCol(Col):
    __kw__ = dict(bSearchable=False, bSortable=False)

    def format(self, item):
        return HTML.img(src=item.jsondata['thumbnail'])


class LicenseCol(Col):
    def __init__(self, dt, name, **kw):
        kw['choices'] = [
            r[0] for r in DBSession.query(ImageData.value)
            .filter(ImageData.key == 'permission')
            .order_by(ImageData.value).distinct()]
        Col.__init__(self, dt, name, **kw)

    def format(self, item):
        return maybe_license_link(self.dt.req, item.get_data('permission') or '')


class Images(DataTable):
    def __init__(self, *args, **kw):
        DataTable.__init__(self, *args, **kw)
        self.License = aliased(ImageData)
        self.Place = aliased(ImageData)

    def base_query(self, query):
        return query\
            .join(self.License, and_(
                self.License.key == 'permission',
                self.License.image_pk == Parameter_files.pk))\
            .join(Parameter_files.object)\
            .options(contains_eager(Parameter_files.object))

    def col_defs(self):
        return [
            MD5Col(self, 'md5', model_col=Parameter_files.id),
            LicenseCol(self, 'license', model_col=self.License.value),
            LinkCol(self, 'species', model_col=Parameter.name, get_object=lambda i: i.object),
            _ThumbnailCol(self, '#'),
        ]

    def get_options(self):
        return dict(sAjaxSource=self.req.route_url('images'))


def includeme(config):
    config.register_datatable('parameters', SpeciesTable)
    config.register_datatable('values', Names)
    config.register_datatable('languages', Languoids)
    config.register_datatable('languages', Languoids)
    config.register_datatable('contributors', TsammalexContributors)
    config.register_datatable('ecoregions', Ecoregions)
    config.register_datatable('images', Images)
