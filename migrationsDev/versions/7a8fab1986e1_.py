"""empty message

Revision ID: 7a8fab1986e1
Revises: 9ee9c6908945
Create Date: 2022-01-22 13:42:20.688182

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a8fab1986e1'
down_revision = '9ee9c6908945'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('invUsuarios',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=45), nullable=True),
    sa.Column('username', sa.String(length=45), nullable=True),
    sa.Column('apellidoPaterno', sa.String(length=45), nullable=True),
    sa.Column('apellidoMaterno', sa.String(length=45), nullable=True),
    sa.Column('password', sa.Text(), nullable=True),
    sa.Column('telefono', sa.String(length=100), nullable=True),
    sa.Column('correo', sa.String(length=100), nullable=True),
    sa.Column('foto', sa.Text(), nullable=True),
    sa.Column('rolId', sa.Integer(), nullable=False),
    sa.Column('statusId', sa.Integer(), nullable=False),
    sa.Column('fechaAlta', sa.DateTime(), nullable=True),
    sa.Column('fechaUltimaModificacion', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['rolId'], ['invRoles.id'], ),
    sa.ForeignKeyConstraint(['statusId'], ['invStatusUsuarios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('invUsuarios')
    # ### end Alembic commands ###
