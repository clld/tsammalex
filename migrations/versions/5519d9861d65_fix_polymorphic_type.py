"""fix polymorphic_type

Revision ID: 5519d9861d65
Revises: 
Create Date: 2014-11-26 15:35:08.895000

"""

# revision identifiers, used by Alembic.
revision = '5519d9861d65'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    update_pmtype(['editor', 'language', 'source', 'value', 'parameter', 'unit'],
        'base', 'custom')


def downgrade():
    update_pmtype(['editor', 'language', 'source', 'value', 'parameter', 'unit'],
        'custom', 'base')


def update_pmtype(tablenames, before, after):
    for table in tablenames:
        op.execute(sa.text('UPDATE %s SET polymorphic_type = :after '
            'WHERE polymorphic_type = :before' % table
            ).bindparams(before=before, after=after))
