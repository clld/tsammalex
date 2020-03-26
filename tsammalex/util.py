from collections import OrderedDict

from purl import URL
from sqlalchemy.orm import joinedload, contains_eager

from clld.web.util.multiselect import MultiSelect
from clld.db.meta import DBSession
from clld.db.models.common import Language, Unit, Value, ValueSet
from clld.web.util.htmllib import HTML
from clld.web.util.helpers import maybe_external_link, collapsed

from tsammalex.models import split_ids
assert split_ids


def license_name(license_url):
    if license_url == "http://commons.wikimedia.org/wiki/GNU_Free_Documentation_License":
        return 'GNU Free Documentation License'
    if license_url == 'http://en.wikipedia.org/wiki/Public_domain':
        license_url = 'http://creativecommons.org/publicdomain/zero/1.0/'
    license_url_ = URL(license_url)
    if license_url_.host() != 'creativecommons.org':
        return license_url

    comps = license_url_.path().split('/')
    if len(comps) < 3:
        return license_url

    return {
        'zero': 'Public Domain',
    }.get(comps[2], '(CC) %s' % comps[2].upper())


def names_in_2nd_languages(vs):
    def format_name(n):
        res = [HTML.i(n.name)]
        if n.ipa:
            res.append('&nbsp;[%s]' % n.ipa)
        return HTML.span(*res)

    def format_language(vs):
        return ' '.join([vs.language.name, ', '.join(format_name(n) for n in vs.values)])

    query = DBSession.query(ValueSet).join(ValueSet.language)\
        .order_by(Language.name)\
        .filter(Language.pk.in_([l.pk for l in vs.language.second_languages]))\
        .filter(ValueSet.parameter_pk == vs.parameter_pk)\
        .options(contains_eager(ValueSet.language), joinedload(ValueSet.values))
    res = '; '.join(format_language(vs) for vs in query)
    if res:
        res = '(%s)' % res
    return res


def source_link(source):
    label = source
    host = URL(source).host()
    if host == 'commons.wikimedia.org':
        label = 'wikimedia'
    elif host == 'en.wikipedia.org':
        label = 'wikipedia'
    return maybe_external_link(source, label=label)


def with_attr(f):
    def wrapper(ctx, name, *args, **kw):
        kw['attr'] = getattr(ctx, name)
        if not kw['attr']:
            return ''  # pragma: no cover
        return f(ctx, name, *args, **kw)
    return wrapper


@with_attr
def tr_rel(ctx, name, label=None, dt='name', dd='description', attr=None):
    content = []
    for item in attr:
        content.extend([HTML.dt(getattr(item, dt)), HTML.dd(getattr(item, dd))])
    content = HTML.dl(*content, class_='dl-horizontal')
    if len(attr) > 3:
        content = collapsed('collapsed-' + name, content)
    return HTML.tr(HTML.td((label or name.capitalize()) + ':'), HTML.td(content))


@with_attr
def tr_attr(ctx, name, label=None, content=None, attr=None):
    return HTML.tr(
        HTML.td((label or name.capitalize()) + ':'),
        HTML.td(content or maybe_external_link(attr)))


def format_classification(taxon, with_species=False, with_rank=False):
    names = OrderedDict()
    for r in 'kingdom phylum class_ order family'.split():
        names[r.replace('_', '')] = getattr(taxon, r)
    if with_species:
        names[taxon.rank] = taxon.name
    return HTML.ul(
        *[HTML.li(('{0} {1}: {2}' if with_rank else '{0}{2}').format('-' * i, *n))
          for i, n in enumerate(n for n in names.items() if n[1])],
        class_="unstyled")


class LanguageMultiSelect(MultiSelect):
    def __init__(self, ctx, req, name='languages', eid='ms-languages', **kw):
        kw['selected'] = ctx.languages
        MultiSelect.__init__(self, req, name, eid, **kw)

    @classmethod
    def query(cls):
        return DBSession.query(Language).order_by(Language.name)

    def get_options(self):
        return {
            'data': [self.format_result(p) for p in self.query()],
            'multiple': True,
            'maximumSelectionSize': 2}


def parameter_index_html(context=None, request=None, **kw):
    return dict(select=LanguageMultiSelect(context, request))


def language_detail_html(context=None, request=None, **kw):
    return dict(categories=list(DBSession.query(Unit)
                .filter(Unit.language == context).order_by(Unit.name)))


def language_index_html(context=None, request=None, **kw):
    return dict(map_=request.get_map('languages', col='lineage', dt=context))
