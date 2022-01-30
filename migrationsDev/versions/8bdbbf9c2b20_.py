"""empty message

Revision ID: 8bdbbf9c2b20
Revises: a3672080d846
Create Date: 2022-01-23 17:42:02.843611

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8bdbbf9c2b20'
down_revision = 'a3672080d846'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('invTipoMoves',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tipo', sa.String(length=45), nullable=True),
    sa.Column('fechaAlta', sa.DateTime(), nullable=True),
    sa.Column('fechaUltimaModificacion', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('invTipoMoves')
    # ### end Alembic commands ###