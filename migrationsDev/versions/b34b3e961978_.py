"""empty message

Revision ID: b34b3e961978
Revises: 8bdbbf9c2b20
Create Date: 2022-01-29 21:36:46.740706

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b34b3e961978'
down_revision = '8bdbbf9c2b20'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('invMovimientos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('idMovimiento', sa.Text(), nullable=True),
    sa.Column('dispositivoId', sa.Integer(), nullable=False),
    sa.Column('usuarioId', sa.Integer(), nullable=False),
    sa.Column('tipoMovId', sa.Integer(), nullable=False),
    sa.Column('LugarId', sa.Integer(), nullable=False),
    sa.Column('comentarios', sa.Text(), nullable=True),
    sa.Column('foto', sa.Text(), nullable=True),
    sa.Column('foto2', sa.Text(), nullable=True),
    sa.Column('fechaAlta', sa.DateTime(), nullable=True),
    sa.Column('fechaUltimaModificacion', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['LugarId'], ['invLugares.id'], ),
    sa.ForeignKeyConstraint(['dispositivoId'], ['invDispositivos.id'], ),
    sa.ForeignKeyConstraint(['tipoMovId'], ['invTipoMoves.id'], ),
    sa.ForeignKeyConstraint(['usuarioId'], ['invUsuarios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('invMovimientos')
    # ### end Alembic commands ###
