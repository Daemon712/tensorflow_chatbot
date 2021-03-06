"""empty message

Revision ID: 4a7acb949aa1
Revises: 90d07d8c385d
Create Date: 2019-06-16 16:29:44.634926

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4a7acb949aa1'
down_revision = '90d07d8c385d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chat', sa.Column('comment', sa.String(length=4096), nullable=True))
    op.add_column('chat', sa.Column('content_rate', sa.Numeric(), nullable=True))
    op.add_column('chat', sa.Column('grammar_rate', sa.Numeric(), nullable=True))
    op.add_column('chat', sa.Column('organization_rate', sa.Numeric(), nullable=True))
    op.add_column('chat', sa.Column('total_rate', sa.Numeric(), nullable=True))
    op.add_column('chat', sa.Column('vocabulary_rate', sa.Numeric(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('chat', 'vocabulary_rate')
    op.drop_column('chat', 'total_rate')
    op.drop_column('chat', 'organization_rate')
    op.drop_column('chat', 'grammar_rate')
    op.drop_column('chat', 'content_rate')
    op.drop_column('chat', 'comment')
    # ### end Alembic commands ###
