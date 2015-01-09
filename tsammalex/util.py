from __future__ import unicode_literals, print_function, absolute_import, division

from sqlalchemy import desc

from clld.web.util.multiselect import MultiSelect
from clld.db.meta import DBSession
from clld.db.models.common import Language, Unit, Identifier
from clld.web.util.htmllib import HTML
from clld.web.util.helpers import maybe_external_link, collapsed, glottolog_url


def tr_rel(ctx, name, label=None, dt='name', dd='description'):
    items = getattr(ctx, name)
    if not items:
        return ''
    content = []
    for item in items:
        content.extend([HTML.dt(getattr(item, dt)), HTML.dd(getattr(item, dd))])
    content = HTML.dl(*content, class_='dl-horizontal')
    if len(items) > 3:
        content = collapsed('collapsed-' + name, content)
    return HTML.tr(HTML.td((label or name.capitalize()) + ':'), HTML.td(content))


def tr_attr(ctx, name, label=None, content=None):
    attr = getattr(ctx, name)
    if not attr:
        return ''
    return HTML.tr(
        HTML.td((label or name.capitalize()) + ':'),
        HTML.td(content or maybe_external_link(attr)))


def format_classification(species, with_species=False, with_rank=False):
    names = [(r, getattr(species, r)) for r in 'kingdom order family genus'.split()]
    if with_species:
        names.append(('species', species.name))
    return HTML.ul(
        *[HTML.li(('{0} {1}: {2}' if with_rank else '{0} {2}').format('-' * i, *n))
          for i, n in enumerate(n for n in names if n[1])],
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
    return dict(categories=DBSession.query(Unit)
                .filter(Unit.language == context).order_by(Unit.name))


def language_index_html(context=None, request=None, **kw):
    return dict(map_=request.get_map('languages', col='lineage', dt=context))
