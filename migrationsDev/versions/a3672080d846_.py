"""empty message

Revision ID: a3672080d846
Revises: 32459e6c9658
Create Date: 2022-01-22 22:45:36.457091

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3672080d846'
down_revision = '32459e6c9658'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('invReportes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dispositivoId', sa.Integer(), nullable=False),
    sa.Column('usuarioId', sa.Integer(), nullable=False),
    sa.Column('comentarios', sa.Text(), nullable=True),
    sa.Column('foto', sa.Text(), nullable=True),
    sa.Column('fechaAlta', sa.DateTime(), nullable=True),
    sa.Column('fechaUltimaModificacion', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['dispositivoId'], ['invDispositivos.id'], ),
    sa.ForeignKeyConstraint(['usuarioId'], ['invUsuarios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('invReportes')
    # ### end Alembic commands ###
