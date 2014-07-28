from clld.web.util.multiselect import MultiSelect
from clld.db.meta import DBSession
from clld.db.models.common import Language


class LanguageMultiSelect(MultiSelect):
    """
    >>> ms = CombinationMultiSelect(None)
    """
    def __init__(self, ctx, req, name='languages', eid='ms-languages', **kw):
        kw['selected'] = ctx.languages
        MultiSelect.__init__(self, req, name, eid, **kw)

    @classmethod
    def query(cls):
        return DBSession.query(Language)

    def get_options(self):
        return {
            'data': [self.format_result(p) for p in self.query()],
            'multiple': True,
            'maximumSelectionSize': 2}


def parameter_index_html(context=None, request=None, **kw):
    return dict(select=LanguageMultiSelect(context, request))
