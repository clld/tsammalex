"""field guides

Revision ID: b25352d6508f
Revises: 3a11c87ddfd7
Create Date: 2018-01-29 10:21:24.851812

"""

# revision identifiers, used by Alembic.
revision = 'b25352d6508f'
down_revision = '3a11c87ddfd7'
branch_labels = None
depends_on = None

import json
import os

import sqlalchemy as sa
from alembic import op

import tsammalex

VPREFIX = 'https://cdstar.shh.mpg.de/bitstreams/'


def upgrade():
    with open(os.path.join(os.path.dirname(tsammalex.__file__),
                           'static', 'field_guides.json')) as fp:
        urlmap = {}

        for k, v in json.load(fp).items():
            urlmap[k] = VPREFIX + v

    for k, v in urlmap.items():
        url = '{"pdf_url": "' + v + '"}'
        query = sa.text(
            'UPDATE language SET jsondata = :jsondata WHERE id = :id'
        ).bindparams(jsondata=url, id=k)

        op.execute(query)


def downgrade():
    pass
