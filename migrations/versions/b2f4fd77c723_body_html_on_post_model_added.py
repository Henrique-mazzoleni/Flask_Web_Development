"""body_html on Post model added

Revision ID: b2f4fd77c723
Revises: 821c9a7f792b
Create Date: 2021-06-19 14:06:28.708969

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2f4fd77c723'
down_revision = '821c9a7f792b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Posts', sa.Column('body_html', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Posts', 'body_html')
    # ### end Alembic commands ###
