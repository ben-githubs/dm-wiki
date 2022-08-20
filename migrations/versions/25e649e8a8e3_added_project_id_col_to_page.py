"""Added project_id col to 'Page'.

Revision ID: 25e649e8a8e3
Revises: c2f45eb88506
Create Date: 2022-08-20 17:03:59.617465

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '25e649e8a8e3'
down_revision = 'c2f45eb88506'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pages', sa.Column('project_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_pages_project_id'), 'pages', ['project_id'], unique=False)
    op.create_foreign_key(None, 'pages', 'projects', ['project_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'pages', type_='foreignkey')
    op.drop_index(op.f('ix_pages_project_id'), table_name='pages')
    op.drop_column('pages', 'project_id')
    # ### end Alembic commands ###
