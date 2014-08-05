from sqlalchemy import desc

from clld.web.util.multiselect import MultiSelect
from clld.db.meta import DBSession
from clld.db.models.common import Language, Unit
from clld.web.util.htmllib import HTML

from tsammalex.models import Languoid


def format_classification(species, with_species=False, with_rank=False):
    names = [(r, getattr(species, r)) for r in 'order family genus'.split()]
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
        return DBSession.query(Language).order_by(
            desc(Languoid.is_english), Language.name)

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
