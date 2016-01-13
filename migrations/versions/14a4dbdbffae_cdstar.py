"""cdstar

Revision ID: 14a4dbdbffae
Revises: 5519d9861d65
Create Date: 2016-01-13 08:01:30.863974

"""

# revision identifiers, used by Alembic.
revision = '14a4dbdbffae'
down_revision = '5519d9861d65'
branch_labels = None
depends_on = None

import os
import json
import tsammalex

from alembic import op
import sqlalchemy as sa

KPREFIX = 'http://edmond.mpdl.mpg.de/imeji/file/d2JGQRxO19XTOEXG/'
VPREFIX = 'https://cdstar.shh.mpg.de/bitstreams/'


def update(pk, urlmap, jsondata):
    n = {}
    for k, v in jsondata.items():
        n[k] = urlmap[v]
    op.execute(
        sa.text('UPDATE parameter_files SET jsondata = :jsondata WHERE pk = :pk')
        .bindparams(jsondata=json.dumps(n), pk=pk))


def upgrade():
    with open(os.path.join(os.path.dirname(tsammalex.__file__), 'static', 'urlmap.json')) as fp:
        urlmap = {}
        for k, v in json.load(fp).items():
            urlmap[KPREFIX + k] = VPREFIX + v

    conn = op.get_bind()
    for pk, jsondata in conn.execute("select pk, jsondata from parameter_files").fetchall():
        update(pk, urlmap, json.loads(jsondata))


def downgrade():
    pass
