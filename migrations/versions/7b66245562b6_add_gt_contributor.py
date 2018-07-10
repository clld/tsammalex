"""add gt contributor

Revision ID: 7b66245562b6
Revises: d99150f4fefc
Create Date: 2018-07-10 15:34:51.522641

"""

# revision identifiers, used by Alembic.
revision = '7b66245562b6'
down_revision = 'd99150f4fefc'
branch_labels = None
depends_on = None

from alembic import op
from clld.db.migration import Connection
from clld.db.models.common import Contributor, Editor

from tsammalex.models import TsammalexContributor, TsammalexEditor


def upgrade():
    conn = Connection(op.get_bind())
    pk = conn.insert(Contributor, id='gt', name='Güldemann, Tom', jsondata={},
                     polymorphic_type='custom',
                     address='Humboldt University of Berlin')
    pke = conn.insert(Editor, jsondata={}, polymorphic_type='custom',
                      dataset_pk=1, contributor_pk=pk)
    conn.insert(TsammalexEditor, pk=pke)
    conn.insert(TsammalexContributor, pk=pk, sections='', research_project='')


def downgrade():
    pass
