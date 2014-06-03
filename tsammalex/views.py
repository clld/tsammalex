from itertools import groupby

from sqlalchemy.orm import joinedload

from clld.db.meta import DBSession

from tsammalex.models import Ecoregion


def ecoregions(req):
    return dict(
        ecoregions=groupby(
            DBSession.query(Ecoregion).order_by(Ecoregion.id).options(joinedload(Ecoregion.species)),
            lambda er: er.description))
